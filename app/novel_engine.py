import json
import datetime
import config
from app.llm_client import llm
from app.database import Session
from app.models import World, Character, Message, PlotEvent, NovelChapter
from app import runtime_config


class NovelEngine:

    @staticmethod
    def generate_chapter(world_id, trigger_reason="plot_advance"):
        session = Session()
        try:
            world = session.query(World).filter(World.id == world_id).first()
            if not world:
                return None

            last_chapter = session.query(NovelChapter).filter(
                NovelChapter.world_id == world_id
            ).order_by(NovelChapter.id.desc()).first()

            last_chapter_time = last_chapter.created_at if last_chapter else None
            last_chapter_num = last_chapter.chapter_num if last_chapter else 0

            if last_chapter_time:
                messages = session.query(Message).filter(
                    Message.world_id == world_id,
                    Message.created_at > last_chapter_time
                ).order_by(Message.id.asc()).all()

                plot_events = session.query(PlotEvent).filter(
                    PlotEvent.world_id == world_id,
                    PlotEvent.created_at > last_chapter_time
                ).order_by(PlotEvent.id.asc()).all()
            else:
                messages = session.query(Message).filter(
                    Message.world_id == world_id
                ).order_by(Message.id.asc()).all()

                plot_events = session.query(PlotEvent).filter(
                    PlotEvent.world_id == world_id
                ).order_by(PlotEvent.id.asc()).all()

            if not messages and not plot_events:
                return None

            if len(messages) < 3 and trigger_reason != "world_end":
                return None

            player = session.query(Character).filter(
                Character.world_id == world_id, Character.role_type == "player"
            ).first()

            npcs = session.query(Character).filter(
                Character.world_id == world_id, Character.role_type == "npc"
            ).all()

            dialogue_summary = "\n".join([
                f"[{m.speaker_name}]: {m.content[:200]}"
                for m in messages[-30:]
            ])

            events_summary = "\n".join([
                f"⚡ {e.title}: {e.description}"
                for e in plot_events
            ])

            npc_snapshot = "\n".join([
                f"  {n.name}({'存活' if n.is_alive else '已死亡'}, {'在场' if n.is_present else '不在场'}): {n.personality[:60]}"
                for n in npcs
            ])

            player_stats_json = "{}"
            if player and player.stats:
                player_stats_json = player.stats if isinstance(player.stats, str) else json.dumps(player.stats, ensure_ascii=False)

            chapter_num = last_chapter_num + 1
            is_final = 1 if trigger_reason == "world_end" else 0

            system_prompt = f"""你是一位精通网文风格的AI作家，笔名「{config.NOVEL_AUTHOR_NAME}」。
你需要将一段多人在线角色扮演的对话记录，改写成一章精彩的网络小说。

网文风格要求：
1. 使用第三人称叙事，叙事流畅自然
2. 对话与叙述穿插，将原始对话转化为小说化对白（融入动作、神态、语气描写）
3. 适当加入心理描写和环境烘托
4. 严禁使用"角色名：对话内容"的格式，所有对话必须融入叙述中
5. 节奏紧凑，段落不宜过长
6. 每章结尾要有悬念或余韵
7. 语言通俗但有文采，不要过于晦涩
8. 角色出场和退场要有画面感，不要简单罗列

输出格式：严格返回JSON"""

            chapter_type_hint = ""
            if is_final:
                chapter_type_hint = "这是最终章，请给这个故事一个合适的结局，回顾主角的旅程，要有收束感。"
            elif trigger_reason == "scene_change":
                chapter_type_hint = "本章重点：场景发生了转换，请着重描写新环境的氛围和冲击感。"
            elif trigger_reason == "npc_leave":
                chapter_type_hint = "本章重点：有角色离开了场景，请着重描写离别时的氛围和众人反应。"
            elif trigger_reason == "npc_enter":
                chapter_type_hint = "本章重点：有新角色入场，请着重描写新角色的登场感及其带来的氛围变化。"
            elif trigger_reason == "npc_death":
                chapter_type_hint = "本章重点：有角色死亡，请着重描写死亡带来的冲击和众人的反应。"
            elif trigger_reason == "plot_advance":
                chapter_type_hint = "本章重点：情节有重要推进，请突出事件的转折和角色的反应。"
            elif trigger_reason == "round_milestone":
                chapter_type_hint = "本章是阶段性回顾，请自然承接上文，对最近发生的事件进行文学化呈现。"

            user_prompt = f"""世界：{world.name}（{world.theme}）
世界观：{world.description}
世界法则：{world.rules}

当前场景：{world.current_scene}
场景描述：{world.scene_description}
情节阶段：{world.plot_stage}

主角：{player.name if player else '未知'} - {player.personality if player else ''}
主角属性：{player_stats_json}

角色一览：
{npc_snapshot}

情节事件：
{events_summary if events_summary else '（无新情节事件）'}

对话记录：
{dialogue_summary}

{chapter_type_hint}

请根据以上内容撰写本章小说，返回JSON：
{{
    "title": "章节标题（5-20字，要有网文感）",
    "content": "本章小说正文（800-2000字），要求符合网文风格，分为多个自然段",
    "summary": "本章摘要（50-150字），概括本章关键情节"
}}"""

            messages_payload = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            result = llm.chat_json(messages_payload, model=runtime_config.model_reasoner(),
                                   temperature=runtime_config.temp_novel(),
                                   max_tokens=runtime_config.tokens_novel())

            if result is None:
                return None

            chapter = NovelChapter(
                world_id=world_id,
                chapter_num=chapter_num,
                title=result.get("title", f"第{chapter_num}章"),
                content=result.get("content", ""),
                summary=result.get("summary", ""),
                trigger_reason=trigger_reason,
                is_final=is_final,
                created_at=datetime.datetime.utcnow()
            )
            session.add(chapter)

            world.novel_chapter_count = chapter_num
            chapter_title = result.get("title", f"第{chapter_num}章")
            chapter_content = result.get("content", "")
            if world.novel_text:
                world.novel_text += f"\n\n{'=' * 30}\n第{chapter_num}章 {chapter_title}\n{'=' * 30}\n\n{chapter_content}"
            else:
                world.novel_text = f"{'=' * 30}\n第{chapter_num}章 {chapter_title}\n{'=' * 30}\n\n{chapter_content}"

            session.commit()

            return {
                "chapter_num": chapter_num,
                "title": result.get("title", ""),
                "summary": result.get("summary", ""),
                "is_final": is_final
            }

        except Exception as e:
            session.rollback()
            print(f"[NovelEngine Error] {e}")
            return None
        finally:
            session.close()

    @staticmethod
    def get_chapters(world_id):
        session = Session()
        try:
            chapters = session.query(NovelChapter).filter(
                NovelChapter.world_id == world_id
            ).order_by(NovelChapter.chapter_num.asc()).all()
            return [c.to_dict() for c in chapters]
        finally:
            session.close()
