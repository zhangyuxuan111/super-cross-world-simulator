import random
import json
import config
from app.llm_client import llm
from app.database import Session
from app import runtime_config
from app.models import World, Character, MemoryEntry


def generate_world(user_suggestion=""):
    theme = random.choice(config.WORLD_GEN_THEME_POOL)

    suggestion_text = f"\n玩家建议倾向：{user_suggestion}" if user_suggestion else ""

    system_prompt = """你是一个世界观创造大师。你需要创造一个独特、有趣、有深度的虚构世界观。
输出严格的JSON格式，不要有任何额外文字。"""

    user_prompt = f"""随机主题：{theme}{suggestion_text}

请创造一个完整的世界观，返回以下JSON结构：
{{
    "theme": "世界主题（中文，5-15字）",
    "name": "这个世界独有的名称（中文，2-8字）",
    "description": "世界观核心描述（200-400字），包括这个世界的基本规则、独特之处",
    "rules": "世界的核心法则（3-5条，每条20-40字）",
    "history": "这个世界的关键历史事件（2-3个，100-200字）",
    "first_scene": "玩家进入的第一个场景名称",
    "scene_description": "开场场景的详细描述（100-200字），需要具有画面感和沉浸感",
    "npcs": [
        {{
            "name": "角色名（中文，1-4字）",
            "personality": "性格描述（30-80字）",
            "background": "角色背景（50-150字）",
            "goals": "角色目标（20-60字）",
            "appearance": "外貌描述（30-80字）",
            "speaking_style": "说话风格（20-50字）",
            "relationship_to_player": "与玩家的初始关系（20-60字）"
        }}
    ]
}}

要求：
1. 世界观要独特有趣，可以混合多种元素（科幻+修仙、末日+童话等）
2. npcs数量3-5个，每个角色要有鲜明的个性和动机
3. 开场场景要有神秘感和吸引力
4. 所有描述用中文"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    result = llm.chat_json(messages, model=runtime_config.model_reasoner(),
                           temperature=runtime_config.temp_creative(),
                           max_tokens=runtime_config.tokens_world())

    if result is None:
        return _fallback_world()

    return result


def _fallback_world():
    return {
        "theme": "赛博朋克修仙",
        "name": "灵境废土",
        "description": "2077年，人类发现了「灵气」这种暗物质能量。修真者与赛博改造者在这片废土上争夺着最后的灵脉资源。",
        "rules": "1.灵气可通过芯片增幅；2.修为越高越容易被黑客入侵；3.灵脉同时是数据节点",
        "history": "大崩坏后，旧文明覆灭。幸存者在废墟中发现了古老的修真法门与先进的科技遗迹。",
        "first_scene": "废弃的数据道观",
        "scene_description": "破败的道观中，全息投影的香火仍在燃烧。损坏的服务器阵列上贴着符箓，发出嗡嗡的低鸣。",
        "npcs": [
            {"name": "灵虚子", "personality": "表面高冷实则热心", "background": "道观最后一位修真者，身体60%已机械化", "goals": "寻找纯正的灵气源头", "appearance": "道袍下露出金属关节", "speaking_style": "古风与现代词汇混合", "relationship_to_player": "对突然出现的你感到好奇"},
            {"name": "赛博娜", "personality": "活泼但警惕", "background": "黑市信息贩子，全身多处义体改造", "goals": "攒够钱去月球殖民地", "appearance": "粉色短发，义眼闪烁蓝光", "speaking_style": "网络用语多，语速快", "relationship_to_player": "想从你身上获取情报价值"},
            {"name": "灵石", "personality": "沉默寡言，忠诚", "background": "一个有自我意识的AI，寄宿在一块灵石中", "goals": "理解人类的修真之道", "appearance": "一块悬浮发光的玉石", "speaking_style": "机械但偶尔有诗意", "relationship_to_player": "认定你为临时宿主"}
        ]
    }


def _to_str(value, default=""):
    if isinstance(value, list):
        return "\n".join(value)
    if value is None:
        return default
    return str(value)


def save_world_to_db(world_data, mode="normal"):
    session = Session()
    session.expire_on_commit = False
    try:
        world = World(
            theme=_to_str(world_data.get("theme")),
            name=_to_str(world_data.get("name")),
            description=_to_str(world_data.get("description")),
            rules=_to_str(world_data.get("rules")),
            history=_to_str(world_data.get("history")),
            current_scene=_to_str(world_data.get("first_scene")),
            scene_description=_to_str(world_data.get("scene_description")),
            plot_stage="intro",
            mode=mode,
            plot_context=json.dumps({"round": 0, "triggers": [], "pending_events": []}, ensure_ascii=False)
        )
        session.add(world)
        session.flush()

        for npc_data in world_data.get("npcs", []):
            char = Character(
                world_id=world.id,
                name=_to_str(npc_data.get("name"), "???"),
                role_type="npc",
                personality=_to_str(npc_data.get("personality")),
                background=_to_str(npc_data.get("background")),
                goals=_to_str(npc_data.get("goals")),
                appearance=_to_str(npc_data.get("appearance")),
                speaking_style=_to_str(npc_data.get("speaking_style")),
                relationships=json.dumps({
                    "player": _to_str(npc_data.get("relationship_to_player"), "陌生人")
                }, ensure_ascii=False),
                stats=json.dumps({}, ensure_ascii=False),
                is_alive=1,
                is_present=1
            )
            session.add(char)
            session.flush()

            mem = MemoryEntry(
                character_id=char.id,
                event_type="world_init",
                content=f"世界「{world.name}」被创造。{char.name}存在于{world.current_scene}。",
                importance=5
            )
            session.add(mem)

        session.commit()
        return world
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def generate_user_character(world, user_suggestion="", player_name_override="", selected_talents=None):
    session = Session()
    try:
        npcs = session.query(Character).filter(
            Character.world_id == world.id, Character.role_type == "npc"
        ).all()
        npc_names = [n.name for n in npcs]

        if selected_talents is None:
            selected_talents = []

        talent_names = [t.get("name", "") for t in selected_talents]
        talent_descriptions = "\n".join([
            f"  {t.get('name', '')}: {t.get('desc', '')}"
            for t in selected_talents
        ]) if selected_talents else "（未选择天赋）"

        system_prompt = """你是一个角色创建大师。根据世界观为玩家创建一个合理的主角角色。
返回严格的JSON格式。"""

        talent_context = ""
        if player_name_override:
            talent_context += f"\n玩家自定义姓名：{player_name_override}"
        if talent_names:
            talent_context += f"""\n玩家已选择以下天赋，请在角色创建中体现：
{talent_descriptions}"""

        user_prompt = f"""世界观：{world.name}（{world.theme}）
世界观描述：{world.description}
法则：{world.rules}
开场场景：{world.current_scene} - {world.scene_description}
已有角色：{', '.join(npc_names)}
玩家建议：{user_suggestion if user_suggestion else '无特殊要求'}{talent_context}

请创建一个与世界观匹配的玩家角色，返回JSON：
{{
    "name": "角色名（中文，1-4字）{'（使用玩家自定义姓名）' if player_name_override else ''}",
    "personality": "基础性格描述（30-80字）",
    "background": "角色背景故事（100-200字），要合理解释为何出现在当前场景，天赋带来的影响也融入其中",
    "appearance": "外貌描述（30-80字）",
    "initial_stats": {{
        "hp": 100, "max_hp": 100,
        "strength": 1-20的整数,
        "intelligence": 1-20的整数,
        "charisma": 1-20的整数,
        "agility": 1-20的整数,
        "luck": 1-20的整数,
        "sanity": 100,
        "inventory": ["随身携带的物品1-3件"],
        "skills": ["初始技能1-2个"],
        "status_effects": []
    }},
    "opening_narration_hint": "旁白开场的提示（30-100字），用世界观中的某个角色的口吻或谜语感的方式"
}}

属性值总和不超过70，保持合理。
{'如果有天赋，请在性格和背景中自然融入天赋的设定，但不要在属性值中直接体现——属性值会在之后自动调整。' if selected_talents else ''}
所有描述用中文。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        result = llm.chat_json(messages, model=runtime_config.model_chat(),
                               temperature=runtime_config.temp_creative(),
                               max_tokens=runtime_config.tokens_world())

        if result is None:
            result = {
                "name": player_name_override or "无名旅者",
                "personality": "谨慎好奇",
                "background": "失去记忆的旅行者",
                "appearance": "普通旅者装扮",
                "initial_stats": config.USER_STATS_TEMPLATE,
                "opening_narration_hint": "又一个迷失的灵魂..."
            }

        if player_name_override:
            result["name"] = player_name_override

        stats = result.get("initial_stats", config.USER_STATS_TEMPLATE)

        for talent in selected_talents:
            effects = talent.get("effects", {})
            for key, val in effects.items():
                if isinstance(val, (int, float)):
                    if key in stats and isinstance(stats.get(key), (int, float)):
                        stats[key] = max(1, stats[key] + val)
                    elif key == "defense":
                        stats["defense"] = (stats.get("defense", 0) + val)
                elif key in ("inventory_slots", "gold"):
                    pass
            if "skills" not in stats:
                stats["skills"] = []
            talent_skill_name = talent.get("name", "")
            if talent_skill_name in ("创造神之力", "神秘戒指", "不死鸟之羽", "傀儡替身",
                                      "避水珠", "通灵玉", "生锈的钥匙", "稻草人",
                                      "天降横财", "虚空储物"):
                if "inventory" not in stats:
                    stats["inventory"] = []
                if talent_skill_name not in stats["inventory"]:
                    stats["inventory"].append(f"[天赋]{talent_skill_name}")

        stats["talents"] = [{"name": t.get("name", ""), "desc": t.get("desc", ""),
                              "type": t.get("type", ""), "effects": t.get("effects", {})}
                             for t in selected_talents]

        player_char = Character(
            world_id=world.id,
            name=_to_str(result.get("name"), "无名者"),
            role_type="player",
            personality=_to_str(result.get("personality")),
            background=_to_str(result.get("background")),
            goals="在这个世界中生存并探索真相",
            appearance=_to_str(result.get("appearance")),
            speaking_style="由玩家自由发挥",
            relationships=json.dumps({n: "初次见面" for n in npc_names}, ensure_ascii=False),
            stats=json.dumps(stats, ensure_ascii=False),
            is_alive=1,
            is_present=1
        )
        session.add(player_char)
        session.commit()

        return result, player_char
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def generate_opening_narration(world, player_name, narration_hint, mode="immersive"):
    session = Session()
    try:
        npcs = session.query(Character).filter(
            Character.world_id == world.id, Character.role_type == "npc", Character.is_present == 1
        ).all()

        npc_descriptions = "\n".join([
            f"- {n.name}：{n.appearance} | {n.personality} | {n.speaking_style}"
            for n in npcs
        ])

        if mode == "normal":
            system_prompt = """你是这个世界的旁白叙述者。用清晰直接的语言欢迎玩家，把该有的信息坦诚地展示出来。
严禁使用"角色名：描述"的格式。所有信息必须融入自然叙述中。

输出格式：直接输出旁白文本，不要加任何前缀。输出2-4段，每段用换行分隔。"""

            user_prompt = f"""世界观：{world.name}（{world.theme}）
世界描述：{world.description}
世界法则：{world.rules}
世界历史：{world.history}

当前场景：{world.current_scene}
场景描述：{world.scene_description}

玩家角色：{player_name}
角色背景：{narration_hint}

场景中的角色：
{npc_descriptions}

请用旁白的形式开始这个世界的故事。要求：
1. 直接清晰地描述这个世界的基本设定和当前场景
2. 明确告诉玩家他们是谁、在哪里、可以做什么
3. 自然地融入在场NPC的描写（融入叙述中，不要用"NPC名："格式罗列）
4. 不要用谜语或隐喻，信息要透明易懂
5. 以引导玩家开始互动的方式结束"""
        else:
            system_prompt = """你是这个世界的旁白叙述者。用文学化的语言为玩家呈现世界。
你的叙述要带有这个世界的独特气质，像是一个知道很多但只透露片段的引导者。
你可以使用谜语、隐喻，或者模拟世界观中某个角色的视角。

输出格式：直接输出旁白文本，不要加任何前缀。输出2-4段，每段用换行分隔。"""

            user_prompt = f"""世界观：{world.name}（{world.theme}）
世界描述：{world.description}
世界法则：{world.rules}
世界历史：{world.history}

当前场景：{world.current_scene}
场景描述：{world.scene_description}

玩家角色：{player_name}
角色背景：{narration_hint}

场景中的角色：
{npc_descriptions}

请用旁白的形式开始这个世界的故事。要求：
1. 用带有这个世界特色的语气叙述
2. 描述当前场景的氛围和细节
3. 暗示但不完全揭示世界观的全部真相
4. 自然地介绍玩家角色的处境
5. 让在场的NPC显得自然存在
6. 以引导玩家开始互动的方式结束"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        narration = llm.chat(messages, model=runtime_config.model_chat(),
                             temperature=runtime_config.temp_narrative(),
                             max_tokens=runtime_config.tokens_narrator())

        return narration or f"欢迎来到{world.name}。{world.scene_description}\n\n你发现自己站在{world.current_scene}中，周围的一切都显得陌生而神秘。"
    finally:
        session.close()


def generate_immersive_opening(world, player_name, player_appearance):
    session = Session()
    try:
        npcs = session.query(Character).filter(
            Character.world_id == world.id, Character.role_type == "npc", Character.is_present == 1
        ).all()

        npc_visuals = "\n".join([
            f"- {n.name}：{n.appearance}"
            for n in npcs
        ])

        system_prompt = """你是一个极简的感官叙述者。你只用视觉、听觉、触觉、嗅觉、味觉来描写这个世界。
**禁止**使用任何说明性文字，不要解释世界观，不要写角色的性格、目标、动机。
不要用"这个世界是..."、"这里是..."之类的说明句式。
严禁使用"角色名：描述"的罗列格式。
像摄影机的镜头一样，只记录你能看到、听到、触摸到的。

输出格式：直接输出感官描写文本，2-4段，每段用换行分隔。"""

        user_prompt = f"""以下信息仅供你理解背景，不要在输出中直接说明：

世界主题：{world.theme}
世界规则（不要直接写出）：{world.rules}

当前场景：{world.current_scene}

玩家：{player_name}，外貌：{player_appearance}

场景中的其他人（只描写他们的外貌，不要写性格）：
{npc_visuals}

请用纯粹的感官描写开始这个故事。要求：
1. 只通过视觉描写环境：看到了什么颜色、形状、光影、物体
2. 通过听觉描写氛围：有什么声音、回响、寂静
3. 通过触觉/嗅觉/温度感受世界：空气是冷是热、有什么气味
4. 描写场景中其他人的外貌、姿态、动作，但不要解释他们是什么样的人
5. 不解释、不说明、不总结。让读者自己感受
6. 最后自然地暗示玩家可以开始行动"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        narration = llm.chat(messages, model=runtime_config.model_chat(),
                             temperature=runtime_config.temp_narrative(),
                             max_tokens=runtime_config.tokens_narrator())

        return narration or f"你睁开眼。\n\n陌生的光线刺入瞳孔。空气中有一股说不清的气味，像铁锈，又像烧焦的糖。\n\n周围有人影晃动，看不清脸。其中一个向你走来。"
    finally:
        session.close()
