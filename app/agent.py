import json
import config
from app.llm_client import llm
from app.database import Session
from app.models import Character, MemoryEntry, Message
from app import runtime_config


class SceneDirector:
    """
    场景导演：分析用户发言后，决定哪些NPC应该回应、回应顺序。
    使用低温度确保决策稳定。
    """

    @staticmethod
    def decide_responses(world, user_message, recent_messages, player_stats):
        session = Session()
        try:
            present_npcs = session.query(Character).filter(
                Character.world_id == world.id,
                Character.role_type == "npc",
                Character.is_alive == 1,
                Character.is_present == 1
            ).all()

            if not present_npcs:
                return []

            npc_info = "\n".join([
                f"id={n.id} | 名={n.name} | 性格={n.personality[:60]} | 目标={n.goals[:60]}"
                for n in present_npcs
            ])

            context = "\n".join([
                f"[{m.speaker_name}]: {m.content[:100]}"
                for m in recent_messages[-6:]
            ])

            system_prompt = """你是一个场景导演。分析玩家发言和当前上下文，决定哪些在场的NPC应该回应。
你必须返回严格的JSON格式。

决策规则：
1. 通常1-3个NPC回应比较自然
2. 如果玩家明确对某个NPC说话，那个NPC必须回应
3. 如果玩家说的话触动了某个NPC的利益/目标/性格，该NPC应回应
4. 有时没有NPC需要直接回应也可以（返回空数组）
5. 排序：最相关的NPC排最前面"""

            user_prompt = f"""世界：{world.name}（{world.theme}）
当前场景：{world.current_scene}

在场NPC：
{npc_info}

最近对话：
{context}

玩家发言：{user_message}

决定哪些NPC应该回应，返回JSON：
{{
    "responders": [
        {{
            "npc_id": 数字,
            "reason": "为什么这个NPC应该回应（10-30字）",
            "action_hint": "这个NPC可能的动作或情绪（10-30字，如：冷笑，走近，警惕地后退）"
        }}
    ],
    "narrator_needed": true/false
}}"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            result = llm.chat_json(messages, model=runtime_config.model_reasoner(),
                                   temperature=runtime_config.temp_director(),
                                   max_tokens=runtime_config.tokens_director())

            if result is None:
                return [{"npc_id": n.id, "reason": "在场", "action_hint": "看向玩家"} for n in present_npcs[:2]]

            responders = result.get("responders", [])
            valid_responders = []
            npc_ids = {n.id for n in present_npcs}
            for r in responders:
                if r.get("npc_id") in npc_ids:
                    valid_responders.append(r)

            return valid_responders
        finally:
            session.close()


class CharacterAgent:
    """
    角色代理：为每个NPC生成符合其设定的对话回复。
    每个角色拥有独立的记忆和上下文。
    """

    @staticmethod
    def generate_response(character, world, user_message, recent_messages, player_name):
        session = Session()
        try:
            memories = session.query(MemoryEntry).filter(
                MemoryEntry.character_id == character.id
            ).order_by(MemoryEntry.id.desc()).limit(config.MAX_MEMORY_ROUNDS).all()

            memory_text = "\n".join([
                f"[记忆-{m.event_type}] {m.content}"
                for m in reversed(memories)
            ])

            context = "\n".join([
                f"[{m.speaker_name}]: {m.content}"
                for m in recent_messages[-8:]
            ])

            relationships = {}
            try:
                relationships = json.loads(character.relationships) if character.relationships else {}
            except:
                pass
            rel_text = "\n".join([f"与{k}的关系：{v}" for k, v in relationships.items()])

            system_prompt = f"""你是{character.name}，你必须严格按照以下设定来进行角色扮演。

=== 世界设定 ===
世界：{world.name}（{world.theme}）
法则：{world.rules}
当前场景：{world.current_scene} - {world.scene_description}

=== 你的角色设定 ===
姓名：{character.name}
性格：{character.personality}
背景：{character.background}
目标：{character.goals}
外貌：{character.appearance}
说话风格：{character.speaking_style}
{rel_text}

=== 行为准则 ===
1. 严格按照你的性格和说话风格来回复
2. 你的回复要符合你的背景知识和目标
3. 你只能知道你的角色应该知道的事情
4. 如果玩家说了不符合世界观的话，你要按照世界观来理解
5. 只输出对话内容本身，严禁在回复中描写任何动作、神态、表情
6. 动作和神态会由旁白系统另外描写，你只需要说话
7. 回复长度适中（20-100字），像真实对话一样自然
8. 不要替其他角色说话
9. 不要替玩家做决定
10. 直接输出纯文本对话，不要加任何前缀或标记"""

            user_prompt = f"""你的记忆：
{memory_text if memory_text else '（暂无重要记忆）'}

最近对话：
{context if context else '（对话刚开始）'}

{player_name}（玩家）对你说或做了以下事情：
{user_message}

请以{character.name}的身份回复。记住你的说话风格：{character.speaking_style}

只输出对话内容，不要描写动作。"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            response = llm.chat(messages, model=runtime_config.model_chat(),
                                temperature=runtime_config.temp_dialogue(),
                                max_tokens=runtime_config.tokens_dialogue())

            if response is None:
                response = "...（沉默）"

            return response
        finally:
            session.close()


def save_memory(character_id, event_type, content, importance=1):
    session = Session()
    try:
        mem = MemoryEntry(
            character_id=character_id,
            event_type=event_type,
            content=content,
            importance=importance
        )
        session.add(mem)
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()


def update_relationship(character_id, target_name, new_relation):
    session = Session()
    try:
        char = session.query(Character).filter(Character.id == character_id).first()
        if char:
            rels = {}
            try:
                rels = json.loads(char.relationships) if char.relationships else {}
            except:
                pass
            rels[target_name] = new_relation
            char.relationships = json.dumps(rels, ensure_ascii=False)
            session.commit()
    except:
        session.rollback()
    finally:
        session.close()
