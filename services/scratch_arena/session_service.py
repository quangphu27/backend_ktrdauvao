"""Logic phiên Scratch Arena — chấm phía server, tách điểm human/AI."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import random
import re

from bson import ObjectId

from database import col
from services.scratch_arena.challenge_bank import AI_PROFILES, DEFAULT_CHALLENGES


def _oid():
    return ObjectId()


def _now():
    return datetime.utcnow()


def ensure_challenges_seeded():
    """Idempotent seed scratch_challenges từ DEFAULT_CHALLENGES."""
    n = 0
    for ch in DEFAULT_CHALLENGES:
        existing = col("scratch_challenges").find_one({"slug": ch["slug"]})
        doc = {**ch, "updated_at": _now()}
        if existing:
            col("scratch_challenges").update_one({"_id": existing["_id"]}, {"$set": doc})
        else:
            doc["created_at"] = _now()
            col("scratch_challenges").insert_one(doc)
            n += 1
    return n


def _public_challenge(doc: dict) -> dict:
    """Ẩn đáp án / solution khi gửi client."""
    out = {
        "id": str(doc["_id"]),
        "slug": doc.get("slug"),
        "round": doc.get("round"),
        "kind": doc.get("kind"),
        "title": doc.get("title"),
        "prompt": doc.get("prompt"),
        "points": int(doc.get("points") or 0),
        "time_limit_sec": int(doc.get("time_limit_sec") or 60),
    }
    if doc.get("blocks"):
        out["blocks"] = doc["blocks"]
    if doc.get("mission"):
        out["mission"] = doc["mission"]
    if doc.get("options"):
        out["options"] = [
            {"id": o["id"], "text": o["text"]} for o in (doc.get("options") or [])
        ]
    return out


def list_challenges(round_num=None):
    ensure_challenges_seeded()
    q = {}
    if round_num is not None:
        q["round"] = int(round_num)
    docs = list(col("scratch_challenges").find(q).sort([("round", 1), ("slug", 1)]))
    return [_public_challenge(d) for d in docs]


def _scratch_course_id():
    course = col("courses").find_one({"slug": "scratch"})
    return str(course["_id"]) if course else None


def fetch_warmup_questions(limit=8):
    """Lấy MCQ Scratch từ ngân hàng questions (read-only). Ẩn đáp án đúng."""
    course_id = _scratch_course_id()
    query = {}
    if course_id:
        query["course_id"] = course_id
    candidates = []
    for doc in col("questions").find(query).limit(200):
        answers = doc.get("answers") or []
        if len(answers) < 2:
            continue
        if not any(a.get("is_correct") for a in answers):
            continue
        content = (doc.get("content") or "").strip()
        if not content:
            continue
        candidates.append(doc)

    random.shuffle(candidates)
    picked = candidates[: max(1, min(limit, len(candidates)))]

    # Fallback: lấy từ quiz Scratch giữa khóa / đầu ra (chỉ options, không lộ correct)
    if len(picked) < 4:
        for quiz in col("quizzes").find(
            {"$or": [{"slug": "scratch-giua-khoa"}, {"slug": "scratch-dau-ra"}, {"title": re.compile("Scratch", re.I)}]}
        ).limit(3):
            for q in quiz.get("questions") or []:
                if q.get("type") != "mcq":
                    continue
                opts = q.get("options") or []
                if len(opts) < 2:
                    continue
                picked.append({
                    "_id": q.get("id") or _oid(),
                    "content": q.get("content"),
                    "answers": [
                        {"id": o.get("id"), "answer_text": o.get("text"), "is_correct": o.get("is_correct")}
                        for o in opts
                    ],
                    "level": "medium",
                })
                if len(picked) >= limit:
                    break
            if len(picked) >= limit:
                break

    public = []
    answer_key = {}
    for doc in picked[:limit]:
        qid = str(doc.get("_id"))
        options = []
        correct_id = None
        for i, a in enumerate(doc.get("answers") or []):
            oid = str(a.get("id") or f"{qid}_{i}")
            text = a.get("answer_text") or a.get("text") or ""
            options.append({"id": oid, "text": text})
            if a.get("is_correct"):
                correct_id = oid
        letters = "ABCD"
        # Chuẩn hóa id A/B/C/D cho UI chuông
        mapped = []
        id_map = {}
        for i, o in enumerate(options[:4]):
            lid = letters[i]
            mapped.append({"id": lid, "text": o["text"]})
            id_map[lid] = o["id"]
            if o["id"] == correct_id:
                answer_key[qid] = lid
        public.append({
            "id": qid,
            "content": re.sub(r"^Câu\s*\d+\s*:\s*", "", doc.get("content") or "", flags=re.I),
            "options": mapped,
            "level": doc.get("level") or "medium",
            "points": 10,
        })
        # lưu map nội bộ trong session sau
        answer_key[f"{qid}__map"] = id_map

    return public, answer_key


def create_session(player_name: str, difficulty: str = "medium", user_id=None):
    ensure_challenges_seeded()
    difficulty = difficulty if difficulty in AI_PROFILES else "medium"
    questions, answer_key = fetch_warmup_questions(8)

    ai_bots = []
    for key in ("easy", "medium", "hard"):
        if difficulty == "easy" and key == "hard":
            continue
        if difficulty == "hard" and key == "easy":
            continue
        prof = AI_PROFILES[key]
        ai_bots.append({
            "id": f"ai_{key}",
            "name": prof["name"],
            "difficulty": key,
            "color": prof["color"],
            "score": 0,
            "is_ai": True,
        })
        if len(ai_bots) >= 3:
            break

    # Luôn 3 AI cho 4 bục (1 người + 3 AI) — điều chỉnh theo difficulty bias
    if len(ai_bots) < 3:
        for key in ("easy", "medium", "hard"):
            if any(b["difficulty"] == key for b in ai_bots):
                continue
            prof = AI_PROFILES[key]
            ai_bots.append({
                "id": f"ai_{key}",
                "name": prof["name"],
                "difficulty": key,
                "color": prof["color"],
                "score": 0,
                "is_ai": True,
            })
            if len(ai_bots) >= 3:
                break

    human = {
        "id": "human",
        "name": (player_name or "Thí sinh").strip()[:40] or "Thí sinh",
        "score": 0,
        "is_ai": False,
        "user_id": user_id,
        "color": "#fbbf24",
    }

    challenges = list(col("scratch_challenges").find({}).sort([("round", 1)]))
    challenge_ids = [str(c["_id"]) for c in challenges]

    doc = {
        "player_name": human["name"],
        "user_id": user_id,
        "difficulty": difficulty,
        "status": "active",
        "round": 1,
        "players": [human] + ai_bots,
        "scores": {p["id"]: 0 for p in [human] + ai_bots},
        "warmup_question_ids": [q["id"] for q in questions],
        "answer_key": answer_key,  # server-only
        "challenge_ids": challenge_ids,
        "events": [],
        "created_at": _now(),
        "updated_at": _now(),
    }
    res = col("scratch_game_sessions").insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc, questions


def get_session(session_id: str):
    try:
        oid = ObjectId(session_id)
    except Exception:
        return None
    return col("scratch_game_sessions").find_one({"_id": oid})


def public_session(doc: dict) -> dict:
    if not doc:
        return None
    return {
        "id": str(doc["_id"]),
        "player_name": doc.get("player_name"),
        "difficulty": doc.get("difficulty"),
        "status": doc.get("status"),
        "round": doc.get("round"),
        "players": doc.get("players") or [],
        "scores": doc.get("scores") or {},
        "created_at": doc.get("created_at").isoformat() + "Z" if doc.get("created_at") else None,
    }


def record_buzz(session_id: str, player_id: str, question_id: str, client_ms: int | None = None):
    doc = get_session(session_id)
    if not doc or doc.get("status") != "active":
        return None, "Phiên không hợp lệ"
    key = f"buzz:{question_id}"
    events = doc.get("events") or []
    if any(e.get("key") == key for e in events):
        winner = next(e for e in events if e.get("key") == key)
        return {"accepted": False, "winner_id": winner.get("player_id"), "already": True}, None

    event = {
        "key": key,
        "type": "buzz",
        "player_id": player_id,
        "question_id": question_id,
        "client_ms": client_ms,
        "at": _now(),
    }
    col("scratch_game_sessions").update_one(
        {"_id": doc["_id"]},
        {"$push": {"events": event}, "$set": {"updated_at": _now()}},
    )
    return {"accepted": True, "winner_id": player_id, "already": False}, None


def grade_warmup_answer(session_id: str, question_id: str, player_id: str, option_id: str):
    doc = get_session(session_id)
    if not doc or doc.get("status") != "active":
        return None, "Phiên không hợp lệ"
    key = answer_key = (doc.get("answer_key") or {}).get(question_id)
    if not key:
        return None, "Không có đáp án cho câu hỏi"
    correct = str(option_id).upper() == str(key).upper()
    points = 10 if correct else 0
    scores = dict(doc.get("scores") or {})
    scores[player_id] = int(scores.get(player_id) or 0) + points
    # sync players[].score
    players = doc.get("players") or []
    for p in players:
        if p.get("id") == player_id:
            p["score"] = scores[player_id]
    col("scratch_game_sessions").update_one(
        {"_id": doc["_id"]},
        {
            "$set": {"scores": scores, "players": players, "updated_at": _now()},
            "$push": {
                "events": {
                    "type": "answer",
                    "question_id": question_id,
                    "player_id": player_id,
                    "option_id": option_id,
                    "correct": correct,
                    "points": points,
                    "at": _now(),
                }
            },
        },
    )
    # submission log
    col("scratch_submissions").insert_one({
        "session_id": str(doc["_id"]),
        "round": 1,
        "kind": "warmup_mcq",
        "player_id": player_id,
        "question_id": question_id,
        "payload": {"option_id": option_id},
        "correct": correct,
        "points": points,
        "is_ai": player_id != "human",
        "created_at": _now(),
    })
    return {
        "correct": correct,
        "points": points,
        "correct_option_id": key,
        "scores": scores,
    }, None


def grade_challenge_submit(session_id: str, challenge_slug: str, player_id: str, payload: dict):
    doc = get_session(session_id)
    if not doc or doc.get("status") != "active":
        return None, "Phiên không hợp lệ"
    ch = col("scratch_challenges").find_one({"slug": challenge_slug})
    if not ch:
        return None, "Không tìm thấy challenge"
    kind = ch.get("kind")
    points = 0
    correct = False
    detail = ""

    if kind == "block_order":
        order = payload.get("order") or []
        expected = ch.get("solution_order") or []
        correct = list(order) == list(expected)
        points = int(ch.get("points") or 0) if correct else 0
        detail = "Khớp thứ tự khối" if correct else "Thứ tự khối chưa đúng"
    elif kind == "mission":
        checks = ch.get("solution_checks") or {}
        ops = payload.get("ops") or []
        must = set(checks.get("must_include") or [])
        any_of = set(checks.get("any_of") or [])
        ok_must = must.issubset(set(ops))
        ok_any = (not any_of) or bool(set(ops) & any_of)
        ok_min = len(ops) >= int(checks.get("min_ops") or 0)
        sim = payload.get("simulation") or {}
        ok_sim = True
        if "stars_needed" in (ch.get("mission") or {}):
            ok_sim = int(sim.get("stars") or 0) >= int(ch["mission"]["stars_needed"])
        if "goal_x" in (ch.get("mission") or {}):
            ok_sim = ok_sim and abs(float(sim.get("x") or 0) - float(ch["mission"]["goal_x"])) < 15
        correct = ok_must and ok_any and ok_min and ok_sim
        points = int(ch.get("points") or 0) if correct else max(0, int((ch.get("points") or 0) * 0.3) if ok_must else 0)
        detail = "Hoàn thành nhiệm vụ" if correct else "Chưa đạt điều kiện nhiệm vụ"
    elif kind == "mcq_hard":
        opt = str(payload.get("option_id") or "").upper()
        correct = opt == str(ch.get("correct_option_id") or "").upper()
        points = int(ch.get("points") or 0) if correct else 0
        detail = "Đúng" if correct else "Sai"
    else:
        return None, "Loại challenge không hỗ trợ"

    scores = dict(doc.get("scores") or {})
    scores[player_id] = int(scores.get(player_id) or 0) + points
    players = doc.get("players") or []
    for p in players:
        if p.get("id") == player_id:
            p["score"] = scores[player_id]

    col("scratch_game_sessions").update_one(
        {"_id": doc["_id"]},
        {
            "$set": {"scores": scores, "players": players, "updated_at": _now()},
            "$push": {
                "events": {
                    "type": "challenge_submit",
                    "slug": challenge_slug,
                    "player_id": player_id,
                    "correct": correct,
                    "points": points,
                    "at": _now(),
                }
            },
        },
    )
    col("scratch_submissions").insert_one({
        "session_id": str(doc["_id"]),
        "round": ch.get("round"),
        "kind": kind,
        "challenge_slug": challenge_slug,
        "player_id": player_id,
        "payload": payload,
        "correct": correct,
        "points": points,
        "is_ai": player_id != "human",
        "created_at": _now(),
    })
    result = {
        "correct": correct,
        "points": points,
        "detail": detail,
        "scores": scores,
    }
    if kind == "mcq_hard":
        result["correct_option_id"] = ch.get("correct_option_id")
    return result, None


def set_round(session_id: str, round_num: int):
    doc = get_session(session_id)
    if not doc:
        return None
    col("scratch_game_sessions").update_one(
        {"_id": doc["_id"]},
        {"$set": {"round": int(round_num), "updated_at": _now()}},
    )
    return get_session(session_id)


def apply_ai_score(session_id: str, player_id: str, points: int):
    """Cộng điểm AI đã được server xác nhận (không tin frontend mù quáng — chỉ AI ids)."""
    doc = get_session(session_id)
    if not doc:
        return None
    if not str(player_id).startswith("ai_"):
        return None
    points = max(0, min(50, int(points)))
    scores = dict(doc.get("scores") or {})
    scores[player_id] = int(scores.get(player_id) or 0) + points
    players = doc.get("players") or []
    for p in players:
        if p.get("id") == player_id:
            p["score"] = scores[player_id]
    col("scratch_game_sessions").update_one(
        {"_id": doc["_id"]},
        {"$set": {"scores": scores, "players": players, "updated_at": _now()}},
    )
    return scores


def finish_session(session_id: str):
    doc = get_session(session_id)
    if not doc:
        return None, "Không tìm thấy phiên"
    scores = doc.get("scores") or {}
    human_score = int(scores.get("human") or 0)
    ranking = sorted(
        [{"id": k, "score": int(v)} for k, v in scores.items()],
        key=lambda x: -x["score"],
    )
    col("scratch_game_sessions").update_one(
        {"_id": doc["_id"]},
        {"$set": {"status": "finished", "round": 4, "updated_at": _now(), "ranking": ranking}},
    )
    # Leaderboard chỉ human
    col("scratch_leaderboard").insert_one({
        "session_id": str(doc["_id"]),
        "player_name": doc.get("player_name"),
        "user_id": doc.get("user_id"),
        "score": human_score,
        "difficulty": doc.get("difficulty"),
        "ranking": ranking,
        "created_at": _now(),
    })
    doc = get_session(session_id)
    return {
        "session": public_session(doc),
        "ranking": ranking,
        "human_score": human_score,
        "winner_id": ranking[0]["id"] if ranking else None,
    }, None


def leaderboard(limit=20):
    docs = list(
        col("scratch_leaderboard").find({}).sort([("score", -1), ("created_at", -1)]).limit(limit)
    )
    return [
        {
            "player_name": d.get("player_name"),
            "score": d.get("score"),
            "difficulty": d.get("difficulty"),
            "created_at": d.get("created_at").isoformat() + "Z" if d.get("created_at") else None,
        }
        for d in docs
    ]
