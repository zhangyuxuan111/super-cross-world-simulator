import json
import os
import time
import threading
import random

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from app.database import Session, engine
from app.models import Base, World, Character, Message, MemoryEntry, NovelChapter, PlotEvent
from app.world_engine import generate_world, save_world_to_db, generate_user_character, generate_opening_narration, generate_immersive_opening
from app.agent import SceneDirector, CharacterAgent, save_memory, update_relationship
from app.plot_engine import PlotEngine
from app.novel_engine import NovelEngine
from app.action_reviewer import ActionReviewer
import config
from app import runtime_config

app = Flask(__name__,
            template_folder=os.path.join(PROJECT_ROOT, "templates"),
            static_folder=os.path.join(PROJECT_ROOT, "static"))
app.config["SECRET_KEY"] = "super-cross-world-sim-secret-key"
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

user_worlds = {}
user_modes = {}


def init_db():
    Base.metadata.create_all(engine)


init_db()


def _get_world_id():
    from flask import request as flask_req
    sid = flask_req.sid
    return user_worlds.get(sid)


def _get_mode():
    from flask import request as flask_req
    sid = flask_req.sid
    return user_modes.get(sid, "normal")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/talents/random", methods=["GET"])
def get_random_talents():
    pool = config.TALENT_POOL
    count = min(7, len(pool))
    selected = random.sample(pool, count)
    return jsonify({"success": True, "talents": selected})


@app.route("/api/world/start", methods=["POST"])
def start_world():
    try:
        data = request.get_json() or {}
        user_suggestion = data.get("suggestion", "")
        mode = data.get("mode", "normal")
        player_name_override = data.get("player_name", "")
        selected_talents = data.get("talents", [])

        world_data = generate_world(user_suggestion)
        if world_data is None:
            return jsonify({"success": False, "error": "世界观生成失败，请重试"}), 500

        world = save_world_to_db(world_data, mode=mode)

        user_char_data, player_char = generate_user_character(
            world, user_suggestion,
            player_name_override=player_name_override,
            selected_talents=selected_talents
        )

        is_immersive = (mode == "immersive")

        if is_immersive:
            narration = generate_immersive_opening(
                world,
                user_char_data.get("name", "无名者"),
                user_char_data.get("appearance", "")
            )
        else:
            narration = generate_opening_narration(
                world,
                user_char_data.get("name", "无名者"),
                user_char_data.get("opening_narration_hint", ""),
                mode="normal"
            )

        session["world_id"] = world.id

        db_session = Session()
        try:
            npcs = db_session.query(Character).filter(
                Character.world_id == world.id, Character.role_type == "npc", Character.is_present == 1
            ).all()
            npc_list = [n.to_dict() for n in npcs]
        finally:
            db_session.close()

        result = {
            "success": True,
            "mode": mode,
            "world": world.to_dict(),
            "player": {
                "name": user_char_data.get("name", "无名者"),
                "personality": user_char_data.get("personality", ""),
                "background": user_char_data.get("background", ""),
                "appearance": user_char_data.get("appearance", ""),
                "stats": user_char_data.get("initial_stats", {})
            },
            "npcs": npc_list if not is_immersive else [],
            "narration": narration
        }

        if is_immersive:
            result["npcs_immersive"] = [
                {"name": n.name, "appearance": n.appearance}
                for n in npcs
            ]
            result["world"] = {
                "id": world.id,
                "name": world.name,
                "theme": world.theme,
                "current_scene": world.current_scene,
                "scene_description": world.scene_description,
                "plot_stage": world.plot_stage,
                "created_at": str(world.created_at)
            }

        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/worlds", methods=["GET"])
def list_worlds():
    db_session = Session()
    try:
        worlds = db_session.query(World).order_by(World.updated_at.desc()).all()
        result = []
        for w in worlds:
            player = db_session.query(Character).filter(
                Character.world_id == w.id, Character.role_type == "player"
            ).first()
            msg_count = db_session.query(Message).filter(
                Message.world_id == w.id
            ).count()
            chapter_count = db_session.query(NovelChapter).filter(
                NovelChapter.world_id == w.id
            ).count()
            result.append({
                "id": w.id,
                "name": w.name,
                "theme": w.theme,
                "current_scene": w.current_scene,
                "plot_stage": w.plot_stage,
                "mode": w.mode or "normal",
                "is_active": w.is_active,
                "player_name": player.name if player else "???",
                "message_count": msg_count,
                "chapter_count": chapter_count,
                "created_at": str(w.created_at),
                "updated_at": str(w.updated_at)
            })
        return jsonify({"success": True, "worlds": result})
    finally:
        db_session.close()


@app.route("/api/world/load/<int:world_id>", methods=["POST"])
def load_world(world_id):
    db_session = Session()
    try:
        world = db_session.query(World).filter(World.id == world_id).first()
        if not world:
            return jsonify({"success": False, "error": "世界不存在"}), 404

        world.is_active = 1
        db_session.commit()

        session["world_id"] = world.id

        player = db_session.query(Character).filter(
            Character.world_id == world.id, Character.role_type == "player"
        ).first()

        npcs = db_session.query(Character).filter(
            Character.world_id == world.id, Character.role_type == "npc"
        ).all()

        messages = db_session.query(Message).filter(
            Message.world_id == world.id
        ).order_by(Message.id.asc()).all()

        return jsonify({
            "success": True,
            "world": world.to_dict(),
            "player": player.to_dict() if player else None,
            "npcs": [n.to_dict() for n in npcs],
            "messages": [m.to_dict() for m in messages]
        })
    finally:
        db_session.close()


@socketio.on("register_session")
def handle_register_session(data):
    from flask import request as flask_req
    sid = flask_req.sid
    user_worlds[sid] = data.get("world_id")
    user_modes[sid] = data.get("mode", "normal")


@app.route("/api/settings", methods=["GET"])
def get_settings():
    return jsonify({"success": True, "settings": runtime_config.get_all()})


@app.route("/api/settings", methods=["POST"])
def update_settings():
    try:
        data = request.get_json() or {}
        updated = runtime_config.update(data)
        return jsonify({"success": True, "settings": updated})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/world/end", methods=["POST"])
def end_world():
    world_id = session.get("world_id")
    if world_id:
        db_session = Session()
        try:
            try:
                NovelEngine.generate_chapter(world_id, trigger_reason="world_end")
            except Exception:
                pass

            world = db_session.query(World).filter(World.id == world_id).first()
            if world:
                db_session.delete(world)
                db_session.commit()
        except Exception as e:
            db_session.rollback()
            import traceback
            traceback.print_exc()
            print(f"[EndWorld Error] {e}")
            return jsonify({"success": False, "error": str(e)}), 500
        finally:
            db_session.close()

    session.pop("world_id", None)
    return jsonify({"success": True, "message": "世界数据已永久删除"})


@app.route("/api/world/apply_talents", methods=["POST"])
def apply_talents():
    world_id = session.get("world_id")
    if not world_id:
        return jsonify({"success": False, "error": "没有活跃的世界"}), 400

    data = request.get_json() or {}
    talents = data.get("talents", [])
    player_name = data.get("player_name", "").strip()

    if not talents or len(talents) != 3:
        return jsonify({"success": False, "error": "需要选择3个天赋"}), 400

    db_session = Session()
    try:
        player = db_session.query(Character).filter(
            Character.world_id == world_id,
            Character.role_type == "player"
        ).first()
        if not player:
            return jsonify({"success": False, "error": "玩家角色不存在"}), 404

        if player_name:
            player.name = player_name

        stats = json.loads(player.stats) if player.stats else {}

        for talent in talents:
            effects = talent.get("effects", {})
            for key, val in effects.items():
                if isinstance(val, (int, float)):
                    if key in stats and isinstance(stats.get(key), (int, float)):
                        stats[key] = max(1, stats[key] + val)
                    elif key == "defense":
                        stats["defense"] = (stats.get("defense", 0) + val)
            talent_name = talent.get("name", "")
            if talent_name in ("创造神之力", "神秘戒指", "不死鸟之羽", "傀儡替身",
                              "避水珠", "通灵玉", "生锈的钥匙", "稻草人",
                              "天降横财", "虚空储物"):
                if "inventory" not in stats:
                    stats["inventory"] = []
                if f"[天赋]{talent_name}" not in stats["inventory"]:
                    stats["inventory"].append(f"[天赋]{talent_name}")

        stats["talents"] = [{"name": t.get("name", ""), "desc": t.get("desc", ""),
                              "type": t.get("type", ""), "effects": t.get("effects", {})}
                             for t in talents]

        player.stats = json.dumps(stats, ensure_ascii=False)
        db_session.commit()

        return jsonify({
            "success": True,
            "player": {
                "name": player.name,
                "personality": player.personality,
                "background": player.background,
                "appearance": player.appearance,
                "stats": stats
            }
        })
    except Exception as e:
        db_session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db_session.close()


@app.route("/api/player/name", methods=["POST"])
def update_player_name():
    world_id = session.get("world_id")
    if not world_id:
        return jsonify({"success": False, "error": "没有活跃的世界"}), 400

    data = request.get_json() or {}
    new_name = data.get("name", "").strip()
    if not new_name or len(new_name) > 8:
        return jsonify({"success": False, "error": "名称需1-8个字符"}), 400

    db_session = Session()
    try:
        player = db_session.query(Character).filter(
            Character.world_id == world_id,
            Character.role_type == "player"
        ).first()
        if not player:
            return jsonify({"success": False, "error": "玩家角色不存在"}), 404
        player.name = new_name
        db_session.commit()
        return jsonify({"success": True, "name": new_name})
    finally:
        db_session.close()


@app.route("/api/novel/chapters", methods=["GET"])
def get_novel_chapters():
    world_id = session.get("world_id")
    if not world_id:
        return jsonify({"success": False, "error": "没有活跃的世界"}), 400

    chapters = NovelEngine.get_chapters(world_id)
    return jsonify({"success": True, "chapters": chapters})


@socketio.on("user_message")
def handle_user_message(data):
    world_id = _get_world_id()
    if not world_id:
        world_id = session.get("world_id")
    if not world_id:
        emit("error", {"message": "没有活跃的世界"})
        return

    user_text = data.get("text", "").strip()
    if not user_text:
        return

    db_session = Session()
    db_session.expire_on_commit = False
    try:
        world = db_session.query(World).filter(World.id == world_id).first()
        if not world or not world.is_active:
            emit("error", {"message": "世界不存在或已结束"})
            return

        player = db_session.query(Character).filter(
            Character.world_id == world_id, Character.role_type == "player"
        ).first()
        if not player:
            emit("error", {"message": "玩家角色不存在"})
            return

        player_stats = json.loads(player.stats) if player.stats else {}

        if not player.is_alive:
            emit("error", {"message": "你已经死亡。"})
            return

        status_effects = player_stats.get("status_effects", [])
        is_restrained = "restrained" in status_effects

        round_num = db_session.query(Message).filter(
            Message.world_id == world_id
        ).count()

        review_result = ActionReviewer.review(world_id, user_text)

        optimized_text = (review_result or {}).get("optimized_text", user_text)
        narrator_comment = (review_result or {}).get("narrator_comment", "")
        action_valid = (review_result or {}).get("action_valid", True)
        player_damage = (review_result or {}).get("player_damage", 0) or 0
        scene_reaction = (review_result or {}).get("scene_reaction", "")

        if is_restrained:
            optimized_text = user_text

        user_msg = Message(
            world_id=world_id,
            round_num=round_num,
            speaker_name=player.name,
            speaker_type="player",
            content=user_text,
            action="",
            created_at=datetime.datetime.utcnow()
        )
        db_session.add(user_msg)
        db_session.commit()

        save_memory(player.id, "dialogue", f"我说：{user_text}", importance=1)

        emit("message_sent", user_msg.to_dict())

        if not action_valid and (review_result or {}).get("reason"):
            reason = review_result["reason"]
            fail_msg = Message(
                world_id=world_id,
                round_num=round_num,
                speaker_name="旁白",
                speaker_type="narrator",
                content=f"⚠️ {reason}",
                action="",
                created_at=datetime.datetime.utcnow()
            )
            db_session.add(fail_msg)
            db_session.commit()
            emit("narrator_message", {**fail_msg.to_dict(), "narrator_type": "action"})

        novel_trigger_reason = None

        if narrator_comment or scene_reaction:
            full_narration = narrator_comment or ""
            if scene_reaction and scene_reaction.strip():
                if full_narration and scene_reaction.strip() not in full_narration:
                    full_narration = full_narration + "\n\n" + scene_reaction
                elif not full_narration:
                    full_narration = scene_reaction

            npc_triggered = (review_result or {}).get("npc_triggered_event")
            if npc_triggered and npc_triggered.get("narration"):
                trig_narr = npc_triggered["narration"].strip()
                if trig_narr and trig_narr not in full_narration:
                    full_narration = full_narration + "\n\n" + trig_narr if full_narration else trig_narr

            npc_reactions = (review_result or {}).get("npc_reactions") or []
            if npc_reactions:
                reaction_parts = []
                for r in npc_reactions:
                    if r and r.get("reaction") and r.get("reaction").strip():
                        reaction_parts.append(r["reaction"].strip())
                if reaction_parts:
                    reaction_text = " ".join(reaction_parts)
                    if reaction_text not in full_narration:
                        full_narration = full_narration + "\n\n" + reaction_text if full_narration else reaction_text

            scene_effect = (review_result or {}).get("scene_effect")
            if scene_effect and scene_effect.get("atmosphere_change"):
                atmos = scene_effect["atmosphere_change"].strip()
                if atmos and atmos not in full_narration and not full_narration.endswith(atmos):
                    full_narration = full_narration + "\n" + atmos if full_narration else atmos

            narrator_msg = Message(
                world_id=world_id,
                round_num=round_num,
                speaker_name="旁白",
                speaker_type="narrator",
                content=full_narration.strip(),
                action="",
                created_at=datetime.datetime.utcnow()
            )
            db_session.add(narrator_msg)
            db_session.commit()
            emit("narrator_message", {**narrator_msg.to_dict(), "narrator_type": "action"})

            scene_effect = (review_result or {}).get("scene_effect")
            if scene_effect and scene_effect.get("scene_changed") and scene_effect.get("new_scene_name"):
                novel_trigger_reason = "scene_change"
                world.current_scene = scene_effect["new_scene_name"]
                world.scene_description = scene_effect.get("new_scene_desc", world.scene_description)
                emit("scene_change", {
                    "new_scene": scene_effect["new_scene_name"],
                    "description": scene_effect.get("new_scene_desc", ""),
                    "transition": scene_effect.get("atmosphere_change", "")
                })

            player_affects = (review_result or {}).get("player_affects_npc")
            if player_affects and player_affects.get("affected_npc"):
                aff_npc = db_session.query(Character).filter(
                    Character.world_id == world_id,
                    Character.name == player_affects["affected_npc"]
                ).first()
                if aff_npc:
                    change_type = player_affects.get("change_type", "")
                    narration = player_affects.get("narration", "")

                    update_relationship(aff_npc.id, player.name,
                                       f"{change_type}: {narration}")
                    save_memory(aff_npc.id, "relation_change",
                                f"对{player.name}：{change_type}。{narration}",
                                importance=4)

                    if "离开" in change_type or "离去" in change_type or "退场" in change_type:
                        aff_npc.is_present = 0
                        db_session.commit()
                        emit("character_change", {
                            "name": aff_npc.name,
                            "type": "leave",
                            "reason": narration[:60]
                        })
                    elif "加入" in change_type or "跟随" in change_type or "入场" in change_type:
                        aff_npc.is_present = 1
                        db_session.commit()
                        emit("character_change", {
                            "name": aff_npc.name,
                            "type": "appear",
                            "reason": narration[:60]
                        })
                    elif "攻击" in change_type:
                        emit("character_change", {
                            "name": aff_npc.name,
                            "type": "attack",
                            "reason": narration[:60]
                        })
                    elif "死亡" in change_type or "杀死" in change_type:
                        novel_trigger_reason = "npc_death"
                        aff_npc.is_alive = 0
                        aff_npc.is_present = 0
                        db_session.commit()
                        save_memory(aff_npc.id, "death", f"死亡。{narration}", importance=5)
                        save_memory(player.id, "plot", f"{aff_npc.name}死了。{narration}", importance=5)
                        emit("character_change", {
                            "name": aff_npc.name,
                            "type": "die",
                            "reason": narration[:60]
                        })

            npc_leave = (review_result or {}).get("npc_leave_scene")
            if npc_leave and npc_leave.get("npc_name"):
                novel_trigger_reason = "npc_leave"
                leave_npc = db_session.query(Character).filter(
                    Character.world_id == world_id,
                    Character.name == npc_leave["npc_name"]
                ).first()
                if leave_npc:
                    leave_npc.is_present = 0
                    db_session.commit()
                    save_memory(leave_npc.id, "departure",
                                f"离开场景。{npc_leave.get('reason', '')}",
                                importance=2)
                    emit("character_change", {
                        "name": leave_npc.name,
                        "type": "leave",
                        "reason": npc_leave.get("reason", "")[:60]
                    })
                    if npc_leave.get("narration"):
                        leave_narr_msg = Message(
                            world_id=world_id,
                            round_num=round_num,
                            speaker_name="旁白",
                            speaker_type="narrator",
                            content=npc_leave["narration"].strip(),
                            action="",
                            created_at=datetime.datetime.utcnow()
                        )
                        db_session.add(leave_narr_msg)
                        db_session.commit()
                        emit("narrator_message", {**leave_narr_msg.to_dict(), "narrator_type": "action"})

            npc_enter = (review_result or {}).get("npc_enter_scene")
            if npc_enter and npc_enter.get("npc_name"):
                novel_trigger_reason = "npc_enter"
                enter_name = npc_enter["npc_name"]
                enter_npc = db_session.query(Character).filter(
                    Character.world_id == world_id,
                    Character.name == enter_name
                ).first()
                if enter_npc:
                    enter_npc.is_present = 1
                    enter_npc.is_alive = 1
                    db_session.commit()
                elif npc_enter.get("is_new") and npc_enter.get("new_npc_data"):
                    nd = npc_enter["new_npc_data"]
                    enter_npc = Character(
                        world_id=world_id,
                        name=str(enter_name),
                        role_type="npc",
                        personality=str(nd.get("personality", "")),
                        background=str(nd.get("background", "")),
                        goals=str(nd.get("goals", "")),
                        appearance=str(nd.get("appearance", "")),
                        speaking_style=str(nd.get("speaking_style", "")),
                        relationships=json.dumps({
                            player.name: str(nd.get("relationship_to_player", "陌生人"))
                        }, ensure_ascii=False),
                        stats=json.dumps({}, ensure_ascii=False),
                        is_alive=1,
                        is_present=1
                    )
                    db_session.add(enter_npc)
                    db_session.commit()
                if enter_npc:
                    emit("character_change", {
                        "name": enter_npc.name,
                        "type": "appear",
                        "reason": npc_enter.get("reason", "")[:60]
                    })
                    if npc_enter.get("narration"):
                        enter_narr_msg = Message(
                            world_id=world_id,
                            round_num=round_num,
                            speaker_name="旁白",
                            speaker_type="narrator",
                            content=npc_enter["narration"].strip(),
                            action="",
                            created_at=datetime.datetime.utcnow()
                        )
                        db_session.add(enter_narr_msg)
                        db_session.commit()
                        emit("narrator_message", {**enter_narr_msg.to_dict(), "narrator_type": "action"})

            if is_restrained and "restrained" in status_effects:
                emit("action_feedback", {
                    "type": "restrained",
                    "message": "你被束缚着，无法自由行动。或许可以尝试呼救或等待救援..."
                })
                emit("processing_done", {"message": "restrained"})
                return

        if player_damage > 0 and player_stats.get("hp", 100) > 0:
            player_stats["hp"] = max(0, player_stats.get("hp", 100) - player_damage)
            player.stats = json.dumps(player_stats, ensure_ascii=False)

            damage_reason = (review_result or {}).get("damage_reason", "")
            emit("stats_update", {
                "stats": player_stats,
                "reason": damage_reason or f"受到 {player_damage} 点伤害"
            })

            if player_stats["hp"] <= 0:
                player.is_alive = 0
                player_stats["status_effects"] = player_stats.get("status_effects", []) + ["dead"]
                player.stats = json.dumps(player_stats, ensure_ascii=False)

                die_msg = Message(
                    world_id=world_id,
                    round_num=round_num,
                    speaker_name="旁白",
                    speaker_type="narrator",
                    content=f"💀 {player.name}倒下了...生命的气息正在消散。",
                    action="",
                    created_at=datetime.datetime.utcnow()
                )
                db_session.add(die_msg)
                db_session.commit()
                emit("narrator_message", {**die_msg.to_dict(), "narrator_type": "plot"})

                save_memory(player.id, "death", "因伤重死亡", importance=10)

                current_plot_context = {}
                try:
                    current_plot_context = json.loads(world.plot_context) if world.plot_context else {}
                except:
                    pass
                death_count = current_plot_context.get("player_death_count", 0) + 1

                if death_count >= 3:
                    revival_type = "permanent_death"
                else:
                    has_game_theme = any(kw in world.theme for kw in ["网游", "游戏", "赛博", "修仙", "魔法", "时间循环", "AI", "数据", "平行"])
                    has_hardcore = any(kw in world.theme for kw in ["末日", "末世", "废土", "现实", "都市"])
                    if has_hardcore and not has_game_theme:
                        revival_type = random.choice(["permanent_death", "revive_plot"])
                    elif has_game_theme:
                        revival_type = random.choice(["revive_game", "revive_magic", "revive_plot"])
                    else:
                        revival_type = random.choice(["revive_magic", "revive_plot", "permanent_death"])

                if revival_type != "permanent_death":
                    revival_messages = {
                        "revive_game": f"一阵数据流包裹了你...你在一处安全区域重新凝聚成形。部分记忆和物品化作光点消散。",
                        "revive_magic": f"冥冥中一股力量将你的灵魂拉回躯壳。你咳出一口浊气，胸口那道致命的伤口正在缓缓愈合。",
                        "revive_plot": f"恍惚间，你感到有人在呼唤你的名字。一双手将你从死亡边缘拉了回来。你虚弱地睁开眼..."
                    }
                    revival_narration = revival_messages.get(revival_type, revival_messages["revive_plot"])

                    player.is_alive = 1
                    player_stats["hp"] = max(1, int(player_stats.get("max_hp", 100) * 0.3))
                    player_stats["status_effects"] = [
                        s for s in player_stats.get("status_effects", []) if s != "dead"
                    ]
                    player.stats = json.dumps(player_stats, ensure_ascii=False)

                    revive_msg = Message(
                        world_id=world_id,
                        round_num=round_num,
                        speaker_name="旁白",
                        speaker_type="narrator",
                        content=f"✨ {revival_narration}",
                        action="",
                        created_at=datetime.datetime.utcnow()
                    )
                    db_session.add(revive_msg)
                    db_session.commit()
                    emit("narrator_message", {**revive_msg.to_dict(), "narrator_type": "plot"})

                    save_memory(player.id, "revive",
                                f"复活。方式：{revival_type}", importance=10)

                    emit("character_change", {
                        "name": player.name,
                        "type": "revive",
                        "reason": revival_narration[:60]
                    })

                    emit("stats_update", {
                        "stats": player_stats,
                        "reason": "复活后恢复少量生命"
                    })

                else:
                    devent = PlotEvent(
                        world_id=world_id,
                        event_type="player_death",
                        title=f"{player.name}永久死亡",
                        description=f"死亡次数：{death_count}。世界即将终结。",
                        changes=json.dumps({"final": True}, ensure_ascii=False)
                    )
                    db_session.add(devent)
                    world.plot_context = json.dumps(
                        {**current_plot_context, "player_death_count": death_count, "final_death": True},
                        ensure_ascii=False
                    )
                    db_session.commit()

                    NovelEngine.generate_chapter(world_id, trigger_reason="world_end")
                    world.is_active = 0
                    db_session.commit()

                    emit("world_ended", {
                        "reason": "player_permanent_death",
                        "message": "你的旅程到此结束。查看小说回味你的冒险吧。"
                    })
                    emit("processing_done", {"message": "world_ended"})
                    return

                current_plot_context["player_death_count"] = death_count
                world.plot_context = json.dumps(current_plot_context, ensure_ascii=False)
                db_session.commit()

                emit("processing_done", {"message": "player_died_revived"})
                return

        recent_messages = db_session.query(Message).filter(
            Message.world_id == world_id
        ).order_by(Message.id.desc()).limit(15).all()
        recent_messages = list(reversed(recent_messages))

        director = SceneDirector()
        responders = director.decide_responses(world, optimized_text, recent_messages, player_stats)

        if not responders:
            plot_result = PlotEngine.check_and_advance(world_id, round_num, recent_messages)
            PlotEngine._emit_plot_events(plot_result, db_session, world_id, player, round_num)
            _handle_novel_generation(world_id, round_num, plot_result, force_reason=novel_trigger_reason)
            emit("processing_done", {"message": "no_response"})
            return

        for i, responder in enumerate(responders):
            npc = db_session.query(Character).filter(Character.id == responder["npc_id"]).first()
            if not npc:
                continue

            emit("typing", {"name": npc.name, "avatar": npc.appearance[:20]})

            time.sleep(1.0)

            agent = CharacterAgent()
            response_text = agent.generate_response(
                npc, world, optimized_text, recent_messages, player.name
            )

            if not response_text:
                response_text = "...（沉默）"

            npc_msg = Message(
                world_id=world_id,
                round_num=round_num,
                speaker_name=npc.name,
                speaker_type="npc",
                content=response_text.strip(),
                action="",
                created_at=datetime.datetime.utcnow()
            )
            db_session.add(npc_msg)
            db_session.commit()

            save_memory(npc.id, "dialogue",
                        f"玩家{player.name}说：{optimized_text[:100]}。我回应：{response_text[:200]}",
                        importance=1)

            update_relationship(npc.id, player.name,
                               f"最近对话：{response_text[:50]}")

            recent_messages.append(npc_msg)

            emit("npc_message", npc_msg.to_dict())

            time.sleep(0.3)

        plot_result = PlotEngine.check_and_advance(world_id, round_num, recent_messages)
        PlotEngine._emit_plot_events(plot_result, db_session, world_id, player, round_num)
        _handle_novel_generation(world_id, round_num, plot_result, force_reason=novel_trigger_reason)

        player_hint = (review_result or {}).get("player_hint", "").strip()
        if player_hint:
            hint_msg = Message(
                world_id=world_id,
                round_num=round_num,
                speaker_name="提示",
                speaker_type="narrator",
                content=player_hint,
                action="",
                created_at=datetime.datetime.utcnow()
            )
            db_session.add(hint_msg)
            db_session.commit()
            emit("narrator_message", {**hint_msg.to_dict(), "narrator_type": "hint"})

        talent_trigger = (review_result or {}).get("talent_trigger")
        if talent_trigger and talent_trigger.get("narration"):
            talent_msg = Message(
                world_id=world_id,
                round_num=round_num,
                speaker_name="天赋触发",
                speaker_type="narrator",
                content=talent_trigger["narration"].strip(),
                action="",
                created_at=datetime.datetime.utcnow()
            )
            db_session.add(talent_msg)
            db_session.commit()
            emit("narrator_message", {**talent_msg.to_dict(), "narrator_type": "talent"})

        emit("processing_done", {"message": "ok"})

    except Exception as e:
        db_session.rollback()
        import traceback
        traceback.print_exc()
        print(f"[Socket Error] {e}")
        emit("error", {"message": f"处理消息时出错：{str(e)}"})
    finally:
        db_session.close()


def _handle_novel_generation(world_id, round_num, plot_result, force_reason=None):
    should_novel = (
        plot_result
        and plot_result.get("should_advance")
        and (
            plot_result.get("scene_change")
            or plot_result.get("plot_event")
            or plot_result.get("character_changes")
        )
    )
    min_rounds_reached = (round_num > 0 and round_num % config.NOVEL_CHAPTER_MIN_ROUNDS == 0)

    if should_novel or min_rounds_reached or force_reason:
        reason = force_reason or ("scene_change" if plot_result and plot_result.get("scene_change") else "plot_advance")
        if min_rounds_reached and not should_novel and not force_reason:
            reason = "round_milestone"
        novel_result = NovelEngine.generate_chapter(world_id, trigger_reason=reason)
        if novel_result:
            emit("novel_chapter", novel_result)


@socketio.on("get_state")
def handle_get_state():
    world_id = _get_world_id()
    if not world_id:
        world_id = session.get("world_id")
    if not world_id:
        emit("state", {"has_world": False})
        return

    mode = _get_mode()

    db_session = Session()
    db_session.expire_on_commit = False
    try:
        world = db_session.query(World).filter(World.id == world_id).first()
        if not world:
            emit("state", {"has_world": False})
            return

        messages = db_session.query(Message).filter(
            Message.world_id == world_id
        ).order_by(Message.id.asc()).all()

        player = db_session.query(Character).filter(
            Character.world_id == world_id, Character.role_type == "player"
        ).first()

        npcs = db_session.query(Character).filter(
            Character.world_id == world_id, Character.role_type == "npc", Character.is_present == 1
        ).all()

        emit("state", {
            "has_world": True,
            "mode": mode,
            "world": world.to_dict(),
            "player": player.to_dict() if player else None,
            "npcs": [n.to_dict() for n in npcs],
            "messages": [m.to_dict() for m in messages]
        })
    finally:
        db_session.close()


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
