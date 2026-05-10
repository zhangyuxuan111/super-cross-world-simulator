import json
import random
import config
from app.llm_client import llm
from app.database import Session
from app.models import World, Character, Message, PlotEvent, MemoryEntry
from app.agent import save_memory, update_relationship
from app import runtime_config


class PlotEngine:

    @staticmethod
    def check_and_advance(world_id, round_num, recent_messages):
        is_scheduled = (round_num % config.PLOT_CHECK_INTERVAL == 0 and round_num > 0)
        is_twist = False
        if not is_scheduled:
            if random.random() < config.PLOT_TWIST_CHANCE and round_num >= 2:
                is_twist = True
            else:
                return None

        session = Session()
        try:
            world = session.query(World).filter(World.id == world_id).first()
            if not world:
                return None

            player = session.query(Character).filter(
                Character.world_id == world_id, Character.role_type == "player"
            ).first()
            if not player:
                return None

            player_stats = json.loads(player.stats) if player.stats else {}
            hp = player_stats.get("hp", 100)
            max_hp = player_stats.get("max_hp", 100)

            npcs = session.query(Character).filter(
                Character.world_id == world_id, Character.role_type == "npc"
            ).all()

            npc_info = "\n".join([
                f"- {n.name}(alive={n.is_alive}, present={n.is_present}): {n.personality[:50]} | goals: {n.goals[:50]}"
                for n in npcs
            ])

            dialogue_summary = "\n".join([
                f"[r{m.round_num}][{m.speaker_name}]: {m.content[:150]}"
                for m in recent_messages[-8:]
            ])

            plot_context = {}
            try:
                plot_context = json.loads(world.plot_context) if world.plot_context else {}
            except:
                pass

            system_prompt = """你是系统情节引擎。你拥有绝对权力驱动剧情，不依赖玩家意愿。

重要能力：
1. 强制场景切换（玩家被绑架/传送/追逐被迫逃离等）
2. 玩家死亡判定（HP归零则死）
3. 玩家被限制行动（束缚、昏迷、被捕等）
4. NPC主动行动（反派袭击、同伴营救、NPC背叛等）
5. 世界事件（天灾、战争、规则异变等）
6. 复活机制判定

决策原则：
- 玩家HP低于20时应考虑危险情节
- 反派NPC会主动出击，不等待玩家
- 情节推动要大胆，不要永远安全
- 玩家死亡后由你决定是否复活及方式
- 如果是网游/修仙/科幻世界观，复活是可能的
- 如果是硬核/末世/现实世界观，死亡更可能是永久的

复活类型：
- "revive_game": 网游复活（新手村重生，失去部分物品经验）
- "revive_magic": 魔法/修仙复活（以某种代价复活）
- "revive_plot": 剧情复活（被同伴救活、被反派复活利用等）
- "permanent_death": 永久死亡，世界终结

返回严格JSON。"""

            twist_instruction = ""
            if is_twist:
                twist_instruction = """\n⚠️ 本轮触发了随机剧情转折！你必须强制推动剧情——从下面选至少一种方式打破现状：
- 一个意想不到的NPC闯入场景
- 环境突然发生危险变化（爆炸、地震、怪物出现等）
- 某个NPC做出出人意料的举动（背叛、告白、暴起攻击等）
- 主角发现了一个重大秘密或线索
- 场景突然切换到另一个地点
请确保 should_advance = true，并填入对应的剧情变化字段。转折要有冲击感但也要合理。"""

            user_prompt = f"""世界：{world.name}（{world.theme}）
世界描述：{world.description}
世界法则：{world.rules}
当前场景：{world.current_scene}
情节阶段：{world.plot_stage}
回合：{round_num}
驱动类型：{'随机剧情转折' if is_twist else '常规情节检查'}

情节上下文：{json.dumps(plot_context, ensure_ascii=False)}

玩家：{player.name}  HP: {hp}/{max_hp}
玩家属性：{json.dumps(player_stats, ensure_ascii=False)}

NPC列表：
{npc_info}

最近对话：
{dialogue_summary}
{twist_instruction}

请判断是否需要系统驱动情节。返回JSON：
{{
    "should_advance": true/false,
    "reason": "原因（20-80字）",

    "player_death": null 或 {{
        "happening": true/false,
        "cause": "死亡原因（20-60字）",
        "death_narration": "死亡描写（80-200字）",
        "revival_type": "permanent_death/revive_game/revive_magic/revive_plot",
        "revival_narration": "复活描写（50-150字，仅非永久死亡时）",
        "revival_cost": "复活的代价（20-60字）"
    }},

    "player_restrained": null 或 {{
        "type": "kidnapped/trapped/arrested/knocked_out",
        "restrain_narration": "被限制的叙述（100-200字）",
        "new_scene": "新场景名",
        "scene_description": "新场景描述",
        "can_act": false,
        "rescue_hint": "营救线索（30-60字，给同伴NPC）"
    }},

    "rescued": null 或 {{
        "rescuer_name": "营救者名（必须是现有NPC名）",
        "rescue_narration": "营救叙述（100-200字）",
        "new_scene": "安全场景名",
        "scene_description": "场景描述"
    }},

    "scene_change": null 或 {{
        "new_scene": "新场景",
        "scene_description": "描述（100-200字）",
        "transition_narration": "转换叙述（50-150字）",
        "forced": true/false
    }},

    "character_changes": [
        {{
            "name": "NPC名",
            "change_type": "leave/die/appear/attack",
            "reason": "原因（20-60字）",
            "new_character_data": null 或 {{"name":"","personality":"","background":"","goals":"","appearance":"","speaking_style":"","relationship_to_player":""}}
        }}
    ],

    "stat_changes": null 或 {{
        "changes": {{}},
        "reason": ""
    }},

    "plot_event": null 或 {{
        "title": "事件标题",
        "description": "事件叙述（50-200字）",
        "type": "revelation/conflict/discovery/twist/danger"
    }},

    "narrator_comment": "旁白（50-150字）"
}}

注意：
- 如果玩家HP<20，应更高概率触发危险事件
- 复活类型要符合世界观。如果是网游世界用revive_game，修仙世界用revive_magic
- 永久死亡只应在硬核世界或玩家多次死亡后发生
- 被限制行动后，应在1-2轮后触发同伴营救
- 不要每轮都推进，但也不要太保守"""
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            result = llm.chat_json(messages, model=runtime_config.model_reasoner(),
                                   temperature=runtime_config.temp_narrative(),
                                   max_tokens=runtime_config.tokens_plot())

            if result is None:
                return None

            if is_twist:
                result["should_advance"] = True
                result["is_twist"] = True
                if not result.get("reason"):
                    result["reason"] = "随机剧情转折触发"

            if not result.get("should_advance"):
                return None

            PlotEngine._apply_changes(session, world, player, npcs, result, round_num)

            return result

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[PlotEngine Error] {e}")
            session.rollback()
            return None
        finally:
            session.close()

    @staticmethod
    def _apply_changes(session, world, player, npcs, result, round_num):
        npc_map = {n.name: n for n in npcs}

        if result.get("new_plot_stage"):
            world.plot_stage = result.get("new_plot_stage")

        player_death = result.get("player_death")
        if player_death and player_death.get("happening"):
            player_stats = json.loads(player.stats) if player.stats else {}
            player_stats["hp"] = 0
            player_stats["status_effects"] = player_stats.get("status_effects", []) + ["dead"]
            player.stats = json.dumps(player_stats, ensure_ascii=False)
            player.is_alive = 0

            devent = PlotEvent(
                world_id=world.id,
                event_type="player_death",
                title=f"{player.name}死亡",
                description=player_death.get("death_narration", ""),
                changes=json.dumps({
                    "revival_type": player_death.get("revival_type", "permanent_death"),
                    "cause": player_death.get("cause", "")
                }, ensure_ascii=False)
            )
            session.add(devent)

            save_memory(player.id, "death",
                        f"玩家死亡。原因：{player_death.get('cause', '')}",
                        importance=10)

            for npc in npcs:
                if npc.is_alive:
                    save_memory(npc.id, "death",
                                f"{player.name}死了。{player_death.get('cause', '')}",
                                importance=9)

            revival = player_death.get("revival_type", "permanent_death")
            if revival != "permanent_death":
                after_death = (
                    player_death.get("revival_narration", "") + "\n" +
                    "代价：" + player_death.get("revival_cost", "无")
                )
                devent2 = PlotEvent(
                    world_id=world.id,
                    event_type="player_revive",
                    title=f"{player.name}复活",
                    description=after_death,
                    changes=json.dumps({"revival_type": revival}, ensure_ascii=False)
                )
                session.add(devent2)

                player.is_alive = 1
                player_stats["hp"] = max(1, int(player_stats.get("max_hp", 100) * 0.3))
                player_stats["status_effects"] = [
                    s for s in player_stats.get("status_effects", []) if s != "dead"
                ]
                player.stats = json.dumps(player_stats, ensure_ascii=False)

                save_memory(player.id, "revive",
                            f"复活了。方式：{revival}。代价：{player_death.get('revival_cost', '')}",
                            importance=10)

        restrained = result.get("player_restrained")
        if restrained:
            rtype = restrained.get("type", "trapped")
            player_stats = json.loads(player.stats) if player.stats else {}
            player_stats["status_effects"] = player_stats.get("status_effects", []) + ["restrained"]
            player.stats = json.dumps(player_stats, ensure_ascii=False)

            if restrained.get("new_scene"):
                world.current_scene = restrained["new_scene"]
                world.scene_description = restrained.get("scene_description", world.scene_description)

            plot_context = {}
            try:
                plot_context = json.loads(world.plot_context) if world.plot_context else {}
            except:
                pass
            plot_context["restrained_type"] = rtype
            plot_context["restrained_round"] = round_num
            world.plot_context = json.dumps(plot_context, ensure_ascii=False)

            save_memory(player.id, "restrained",
                        f"被{rtype}在{world.current_scene}。{restrained.get('restrain_narration', '')[:200]}",
                        importance=8)

        rescued = result.get("rescued")
        if rescued:
            player_stats = json.loads(player.stats) if player.stats else {}
            player_stats["status_effects"] = [
                s for s in player_stats.get("status_effects", []) if s != "restrained"
            ]
            player.stats = json.dumps(player_stats, ensure_ascii=False)

            if rescued.get("new_scene"):
                world.current_scene = rescued["new_scene"]
                world.scene_description = rescued.get("scene_description", world.scene_description)

            rescuer_name = rescued.get("rescuer_name", "")
            save_memory(player.id, "rescued",
                        f"被{rescuer_name}营救。{rescued.get('rescue_narration', '')[:200]}",
                        importance=8)

            if rescuer_name in npc_map:
                save_memory(npc_map[rescuer_name].id, "rescued_player",
                            f"营救了{player.name}。{rescued.get('rescue_narration', '')[:200]}",
                            importance=7)

            plot_context = {}
            try:
                plot_context = json.loads(world.plot_context) if world.plot_context else {}
            except:
                pass
            plot_context.pop("restrained_type", None)
            plot_context.pop("restrained_round", None)
            world.plot_context = json.dumps(plot_context, ensure_ascii=False)

        scene_change = result.get("scene_change")
        if scene_change:
            world.current_scene = scene_change.get("new_scene", world.current_scene)
            world.scene_description = scene_change.get("scene_description", world.scene_description)
            for npc in npcs:
                if npc.is_alive:
                    save_memory(npc.id, "scene",
                                f"场景切换：{scene_change.get('transition_narration', '')}",
                                importance=3)

        for change in (result.get("character_changes") or []):
            if not change:
                continue
            name = change.get("name", "")
            change_type = change.get("change_type", "")

            if change_type == "die" and name in npc_map:
                npc = npc_map[name]
                npc.is_alive = 0
                npc.is_present = 0
                save_memory(npc.id, "death",
                            f"死亡。{change.get('reason', '')}", importance=5)
                save_memory(player.id, "plot",
                            f"{npc.name}死了。{change.get('reason', '')}", importance=5)

            elif change_type == "leave" and name in npc_map:
                npc = npc_map[name]
                npc.is_present = 0
                save_memory(npc.id, "departure",
                            f"离开。{change.get('reason', '')}", importance=2)

            elif change_type == "attack" and name in npc_map:
                npc = npc_map[name]
                save_memory(player.id, "danger",
                            f"{npc.name}发起攻击！{change.get('reason', '')}", importance=7)
                save_memory(npc.id, "attack",
                            f"攻击了{player.name}。{change.get('reason', '')}", importance=6)

            elif change_type == "appear":
                new_data = change.get("new_character_data") or {}
                if new_data.get("name"):
                    existing = session.query(Character).filter(
                        Character.world_id == world.id,
                        Character.name == new_data["name"]
                    ).first()
                    if existing:
                        existing.is_present = 1
                        existing.is_alive = 1
                    else:
                        new_char = Character(
                            world_id=world.id,
                            name=str(new_data.get("name", "???")),
                            role_type="npc",
                            personality=str(new_data.get("personality", "")),
                            background=str(new_data.get("background", "")),
                            goals=str(new_data.get("goals", "")),
                            appearance=str(new_data.get("appearance", "")),
                            speaking_style=str(new_data.get("speaking_style", "")),
                            relationships=json.dumps({
                                "player": str(new_data.get("relationship_to_player", "陌生人"))
                            }, ensure_ascii=False),
                            stats=json.dumps({}, ensure_ascii=False),
                            is_alive=1,
                            is_present=1
                        )
                        session.add(new_char)
                        session.flush()

        stat_changes = result.get("stat_changes") or {}
        if stat_changes and stat_changes.get("changes"):
            current_stats = json.loads(player.stats) if player.stats else {}
            changes = stat_changes.get("changes", {})
            reason = stat_changes.get("reason", "")

            for key in ["hp", "max_hp", "strength", "intelligence", "charisma", "agility", "luck", "sanity"]:
                if key in changes and isinstance(changes[key], (int, float)):
                    old_val = current_stats.get(key, 0)
                    current_stats[key] = max(0, min(999, old_val + changes[key]))

            inv_add = changes.get("inventory_add")
            if inv_add:
                inv = current_stats.get("inventory", [])
                if isinstance(inv_add, list):
                    inv.extend([str(i) for i in inv_add])
                elif isinstance(inv_add, str):
                    inv.append(inv_add)
                current_stats["inventory"] = inv

            skills_add = changes.get("skills_add")
            if skills_add:
                skills = current_stats.get("skills", [])
                if isinstance(skills_add, list):
                    skills.extend([str(s) for s in skills_add])
                elif isinstance(skills_add, str):
                    skills.append(skills_add)
                current_stats["skills"] = skills

            player.stats = json.dumps(current_stats, ensure_ascii=False)
            save_memory(player.id, "stat_change",
                        f"属性变化：{json.dumps(changes, ensure_ascii=False)}。{reason}",
                        importance=3)

        plot_event = result.get("plot_event")
        if plot_event:
            event = PlotEvent(
                world_id=world.id,
                event_type=plot_event.get("type", "plot_twist"),
                title=plot_event.get("title", ""),
                description=plot_event.get("description", ""),
                changes=json.dumps(result.get("stat_changes") or {}, ensure_ascii=False)
            )
            session.add(event)

        plot_context = {}
        try:
            plot_context = json.loads(world.plot_context) if world.plot_context else {}
        except:
            pass
        plot_context["round"] = round_num
        plot_context["last_advance_reason"] = result.get("reason", "")
        plot_context["player_death_count"] = plot_context.get("player_death_count", 0)
        if result.get("player_death", {}).get("happening"):
            plot_context["player_death_count"] += 1
        world.plot_context = json.dumps(plot_context, ensure_ascii=False)

        session.commit()

    @staticmethod
    def _emit_plot_events(plot_result, db_session, world_id, player, round_num):
        if not plot_result:
            return

        from flask_socketio import emit
        import datetime

        narrator_comment = plot_result.get("narrator_comment") or ""

        player_death = plot_result.get("player_death")
        if player_death and player_death.get("happening"):
            death_narr = player_death.get("death_narration", "")
            die_msg = Message(
                world_id=world_id,
                round_num=round_num,
                speaker_name="旁白",
                speaker_type="narrator",
                content=f"💀 {death_narr}",
                action="",
                created_at=datetime.datetime.utcnow()
            )
            db_session.add(die_msg)
            db_session.commit()
            emit("narrator_message", {**die_msg.to_dict(), "narrator_type": "plot"})

            revival = player_death.get("revival_type", "permanent_death")
            if revival != "permanent_death":
                after_narr = player_death.get("revival_narration", "")
                cost = player_death.get("revival_cost", "")
                full_revive = after_narr + ("\n代价：" + cost if cost else "")
                revive_msg = Message(
                    world_id=world_id,
                    round_num=round_num,
                    speaker_name="旁白",
                    speaker_type="narrator",
                    content=f"✨ {full_revive}",
                    action="",
                    created_at=datetime.datetime.utcnow()
                )
                db_session.add(revive_msg)
                db_session.commit()
                emit("narrator_message", {**revive_msg.to_dict(), "narrator_type": "plot"})

                emit("character_change", {
                    "name": player.name,
                    "type": "revive",
                    "reason": after_narr[:60]
                })

                player_stats = json.loads(player.stats) if player.stats else {}
                emit("stats_update", {
                    "stats": player_stats,
                    "reason": "复活后恢复少量生命"
                })
            else:
                from app.novel_engine import NovelEngine
                world = db_session.query(World).filter(World.id == world_id).first()
                if world:
                    NovelEngine.generate_chapter(world_id, trigger_reason="world_end")
                    world.is_active = 0
                    db_session.commit()
                emit("world_ended", {
                    "reason": "player_permanent_death",
                    "message": "你的旅程到此结束。查看小说回味你的冒险吧。"
                })
                return

        restrained = plot_result.get("player_restrained")
        if restrained:
            rnarration = restrained.get("restrain_narration", "")
            restrain_msg = Message(
                world_id=world_id,
                round_num=round_num,
                speaker_name="旁白",
                speaker_type="narrator",
                content=rnarration,
                action="",
                created_at=datetime.datetime.utcnow()
            )
            db_session.add(restrain_msg)
            db_session.commit()
            emit("narrator_message", {**restrain_msg.to_dict(), "narrator_type": "plot"})

            emit("action_feedback", {
                "type": "restrained",
                "message": "你被束缚着，无法自由行动。或许可以尝试呼救或等待救援..."
            })

            if restrained.get("new_scene"):
                emit("scene_change", {
                    "new_scene": restrained["new_scene"],
                    "description": restrained.get("scene_description", ""),
                    "transition": rnarration[:100]
                })

        rescued = plot_result.get("rescued")
        if rescued:
            rescue_narr = rescued.get("rescue_narration", "")
            rescue_msg = Message(
                world_id=world_id,
                round_num=round_num,
                speaker_name="旁白",
                speaker_type="narrator",
                content=rescue_narr,
                action="",
                created_at=datetime.datetime.utcnow()
            )
            db_session.add(rescue_msg)
            db_session.commit()
            emit("narrator_message", {**rescue_msg.to_dict(), "narrator_type": "plot"})

            if rescued.get("new_scene"):
                emit("scene_change", {
                    "new_scene": rescued["new_scene"],
                    "description": rescued.get("scene_description", ""),
                    "transition": rescue_narr[:100]
                })

            emit("action_feedback", {
                "type": "rescued",
                "message": f"你被{rescued.get('rescuer_name', '同伴')}救了出来！"
            })

        if narrator_comment and not restrained and not player_death and not rescued:
            narrator_msg = Message(
                world_id=world_id,
                round_num=round_num,
                speaker_name="旁白",
                speaker_type="narrator",
                content=narrator_comment,
                action="",
                created_at=datetime.datetime.utcnow()
            )
            db_session.add(narrator_msg)
            db_session.commit()
            emit("narrator_message", {**narrator_msg.to_dict(), "narrator_type": "plot"})

        if plot_result.get("character_changes"):
            for change in (plot_result.get("character_changes") or []):
                if not change:
                    continue
                emit("character_change", {
                    "name": change.get("name", ""),
                    "type": change.get("change_type", ""),
                    "reason": change.get("reason", "")
                })

        scene_change = plot_result.get("scene_change") or {}
        if scene_change and not restrained and not rescued:
            emit("scene_change", {
                "new_scene": scene_change.get("new_scene", ""),
                "description": scene_change.get("scene_description", ""),
                "transition": scene_change.get("transition_narration", "")
            })

        stat_changes = plot_result.get("stat_changes") or {}
        if stat_changes.get("changes"):
            updated_player = db_session.query(Character).filter(
                Character.id == player.id
            ).first()
            if updated_player:
                emit("stats_update", {
                    "stats": json.loads(updated_player.stats) if updated_player and updated_player.stats else {},
                    "reason": stat_changes.get("reason", "")
                })

        if plot_result.get("plot_event"):
            emit("plot_event", plot_result["plot_event"])

        if plot_result.get("is_twist"):
            emit("plot_twist", {
                "reason": plot_result.get("reason", "剧情转折"),
                "narrator_comment": narrator_comment[:100]
            })
