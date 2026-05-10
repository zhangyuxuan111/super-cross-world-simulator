import json
from app.llm_client import llm
from app.database import Session
from app.models import World, Character, Message
from app import runtime_config


class ActionReviewer:

    @staticmethod
    def review(world_id, user_text):
        session = Session()
        try:
            world = session.query(World).filter(World.id == world_id).first()
            if not world:
                return None

            player = session.query(Character).filter(
                Character.world_id == world_id, Character.role_type == "player"
            ).first()

            npcs = session.query(Character).filter(
                Character.world_id == world_id, Character.role_type == "npc", Character.is_present == 1
            ).all()

            npc_info = "\n".join([
                f"  {n.name}(alive={n.is_alive}): personality={n.personality[:60]} goals={n.goals[:60]}"
                for n in npcs
            ])

            player_stats = json.loads(player.stats) if player and player.stats else {}
            hp = player_stats.get("hp", 100)
            max_hp = player_stats.get("max_hp", 100)
            status = player_stats.get("status_effects", [])

            recent_msgs = session.query(Message).filter(
                Message.world_id == world_id
            ).order_by(Message.id.desc()).limit(10).all()
            recent_msgs = list(reversed(recent_msgs))
            recent_context = "\n".join([
                f"[{m.speaker_name}({m.speaker_type})]: {m.content[:150]}"
                for m in recent_msgs
            ])

            talents_info = ""
            player_talents = player_stats.get("talents", [])
            if player_talents:
                talent_lines = []
                for t in player_talents:
                    name = t.get("name", "")
                    desc = t.get("desc", "")
                    effects = t.get("effects", {})
                    talent_lines.append(f"  · {name}：{desc}（效果：{json.dumps(effects, ensure_ascii=False)}）")
                talents_info = "\n主角天赋：\n" + "\n".join(talent_lines) + "\n"

            system_prompt = """你是这个世界的行动仲裁者和场景叙述者。你审查玩家的行为，同时监测在场角色之间的互动关系。

你需要完成以下任务：

1. **行为审查**：玩家行为是否在当前世界观、场景、角色能力下可行
2. **话语优化**：将玩家的原始输入改写为更符合角色性格和世界观风格的表达
3. **旁白叙述**：描述行为产生后的环境变化、氛围、物理反应
4. **NPC→主角影响**：检测在场NPC是否因玩家的行为而采取行动
5. **主角→NPC影响**：检测玩家的行为是否对在场NPC产生了影响
6. **场景变化**：判断当前行为是否导致场景的自然变化
7. **NPC自主引发**：检测在场的NPC是否会主动触发事件
8. **天赋触发检测**：检查主角本轮的行为是否触发了某个天赋的效果，如果触发则描述

返回严格JSON格式。"""

            user_prompt = f"""世界：{world.name}（{world.theme}）
世界观：{world.description}
世界法则：{world.rules}
当前场景：{world.current_scene} - {world.scene_description}
情节阶段：{world.plot_stage}

主角：{player.name if player else '???'}
性格：{player.personality if player else ''}
外貌：{player.appearance if player else ''}
生命值：{hp}/{max_hp}
状态：{json.dumps(status, ensure_ascii=False)}
{talents_info}

在场NPC：
{npc_info}

最近对话历史：
{recent_context if recent_context else '（故事刚开始）'}

玩家原始输入：{user_text}

请审查并返回JSON：
{{
    "action_valid": true/false,
    "reason": "如果不可行，说明原因（20-60字）",
    "optimized_text": "优化后的行为/话语（保持原意，符合角色性格和世界观风格，20-200字）",

    "narrator_comment": "旁白描述（50-200字）：描述行为的环境变化、氛围、感官细节",
    "player_damage": 0,
    "damage_reason": "伤害原因",
    "scene_reaction": "场景对本轮互动的整体反应（30-100字）",

    "npc_triggered_event": null 或 {{
        "trigger_npc": "发起事件的NPC名字（必须是在场NPC之一）",
        "event_type": "attack/help/observe/betray/faint/offer_info/emotional_reaction",
        "narration": "NPC引发的事件叙述（50-150字），描述这个NPC做了什么，以及环境和他人的反应"
    }},

    "npc_reactions": [
        {{
            "npc_name": "NPC名（必须与在场NPC匹配）",
            "reaction": "该NPC对玩家行为的纯客观反应描写（20-60字），不要用\"NPC名：\"前缀。示例：'铁匠王五抬眼瞥了一眼，摇了摇头'而不是'铁匠王五摇了摇头'",
            "affects_player": true/false,
            "effect_on_player": "如果影响玩家，说明影响（如：获得信任/激怒/使其离开/使其攻击）"
        }}
    ],

    "scene_effect": null 或 {{
        "scene_changed": true/false,
        "new_scene_name": "新场景名（仅当场景确实变化时，如：从酒馆大厅→酒馆后院）",
        "new_scene_desc": "新场景描述（30-80字）",
        "atmosphere_change": "氛围变化描述（20-60字），如：原本热闹的酒馆突然安静下来"
    }},

    "player_affects_npc": null 或 {{
        "affected_npc": "受影响的NPC名",
        "change_type": "好感上升/好感下降/信任/敌意/恐惧/离开/加入/跟随/攻击/死亡",
        "narration": "影响描述（20-60字）"
    }},

    "npc_leave_scene": null 或 {{
        "npc_name": "离开的NPC名",
        "reason": "离开原因（10-30字）",
        "narration": "离开的描写（20-60字），纯客观叙述，如：'铁匠王五摇了摇头，转身消失在人群中'"
    }},

    "npc_enter_scene": null 或 {{
        "npc_name": "进入场景的NPC名（可以是新NPC或重新出现的旧NPC）",
        "is_new": true/false,
        "reason": "出现原因（10-30字）",
        "narration": "出现的描写（20-60字），纯客观叙述",
        "new_npc_data": null 或 {{"personality":"","background":"","goals":"","appearance":"","speaking_style":"","relationship_to_player":""}}
    }},

    "forced_event": null,

    "player_hint": "给玩家的白话建议（20-40字），用最直白的语言告诉玩家可以做什么。示例：'老铁匠好像知道些什么，不如去问问他关于那把剑的事。'或者'这里太危险了，先退回安全的地方想想办法。'",

    "talent_trigger": null 或 {{
        "talent_name": "被触发的天赋名（必须与主角天赋列表中的名字匹配）",
        "trigger_reason": "本轮什么行为/事件触发了该天赋（10-30字）",
        "narration": "天赋触发的描写（20-50字），纯客观叙述。如：'神秘戒指微微发光，一股暖流护住了他的心脉。'"
    }}
}}

注意：
- npc_triggered_event用于NPC主动发起的事件（不依赖玩家行为）
- npc_reactions中的reaction必须是纯客观描写，包含NPC名在内。如：'铁匠王五皱起眉头，手指在铁砧上敲了两下'而不是'对玩家的行为感到不满'
- 场景反应要具体且有画面感
- 角色离场或入场时填写npc_leave_scene或npc_enter_scene
- 角色之间的互动要通过具体动作和神态来表现，不要简单概括
- talent_trigger用于主角的天赋在本轮被触发时，描写天赋发挥效果的细节
- 天赋触发要合理：战斗类天赋在战斗时触发、社交类天赋在谈判时触发、回复类天赋在受伤时触发等"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            result = llm.chat_json(messages, model=runtime_config.model_reasoner(),
                                   temperature=0.7,
                                   max_tokens=3072)

            if result is None:
                return {
                    "action_valid": True,
                    "reason": "",
                    "optimized_text": user_text,
                    "narrator_comment": "",
                    "player_damage": 0,
                    "damage_reason": "",
                    "scene_reaction": "",
                    "npc_triggered_event": None,
                    "npc_reactions": [],
                    "scene_effect": None,
                    "player_affects_npc": None,
                    "forced_event": None
                }

            return result

        except Exception as e:
            print(f"[ActionReviewer Error] {e}")
            return {
                "action_valid": True,
                "reason": "",
                "optimized_text": user_text,
                "narrator_comment": "",
                "player_damage": 0,
                "damage_reason": "",
                "scene_reaction": "",
                "npc_triggered_event": None,
                "npc_reactions": [],
                "scene_effect": None,
                "player_affects_npc": None,
                "forced_event": None
            }
        finally:
            session.close()
