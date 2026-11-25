"""Tạo attempt, chấm server-side, leaderboard — collection IQ300Attempts."""

from __future__ import annotations

from datetime import datetime
import random
from typing import Any

from bson import ObjectId

from database import col
from services.iq300.catalog import (
    CHALLENGES,
    get_challenge,
    public_challenges,
    rank_title,
)

COLL = "IQ300Attempts"


def _now():
    return datetime.utcnow()


def create_attempt(payload: dict, user_id=None) -> dict:
    name = (payload.get("full_name") or payload.get("name") or "").strip()[:80]
    clazz = (payload.get("class_name") or payload.get("clazz") or "").strip()[:40]
    grade = str(payload.get("grade") or "").strip()
    if grade not in ("6", "7"):
        raise ValueError("Khối phải là 6 hoặc 7")
    if not name:
        raise ValueError("Thiếu họ tên")

    light_idx = random.randint(0, 8)
    doc = {
        "full_name": name,
        "class_name": clazz,
        "grade": grade,
        "user_id": user_id,
        "status": "in_progress",
        "started_at": _now(),
        "finished_at": None,
        "current_index": 1,
        "answers": {},
        "per_question": [],
        "total_score": 0,
        "correct_count": 0,
        "duration_sec": None,
        "light_coin_index": light_idx,  # server secret for Q8
        "submitted": False,
        "created_at": _now(),
        "updated_at": _now(),
    }
    res = col(COLL).insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc


def get_attempt(attempt_id: str):
    try:
        oid = ObjectId(attempt_id)
    except Exception:
        return None
    return col(COLL).find_one({"_id": oid})


def public_attempt(doc: dict, include_review=False) -> dict:
    if not doc:
        return None
    out = {
        "id": str(doc["_id"]),
        "full_name": doc.get("full_name"),
        "class_name": doc.get("class_name"),
        "grade": doc.get("grade"),
        "status": doc.get("status"),
        "started_at": _iso(doc.get("started_at")),
        "finished_at": _iso(doc.get("finished_at")),
        "current_index": doc.get("current_index"),
        "total_score": doc.get("total_score"),
        "correct_count": doc.get("correct_count"),
        "duration_sec": doc.get("duration_sec"),
        "rank_title": rank_title(doc.get("total_score") or 0),
        "max_score": 150,
        "answered_ids": sorted(int(k) for k in (doc.get("answers") or {}).keys()),
    }
    if include_review and doc.get("status") == "finished":
        out["per_question"] = doc.get("per_question") or []
    return out


def _iso(dt):
    if not dt:
        return None
    if isinstance(dt, datetime):
        return dt.isoformat() + "Z"
    return str(dt)


def grade_answer(attempt_id: str, question_id: int, answer: Any, reaction_ms=None):
    doc = get_attempt(attempt_id)
    if not doc:
        return None, "Không tìm thấy lượt chơi"
    if doc.get("status") != "in_progress" or doc.get("submitted"):
        return None, "Lượt chơi đã kết thúc"
    ch = get_challenge(question_id)
    if not ch:
        return None, "Câu hỏi không hợp lệ"
    key = str(question_id)
    if key in (doc.get("answers") or {}):
        return None, "Câu này đã trả lời, không sửa được"

    expected = ch.get("correct")
    points = 0
    is_correct = False
    detail = ""

    if ch["kind"] == "balance":
        # answer: { identified_coin: 0..8, weighings: [...] }
        if not isinstance(answer, dict):
            return None, "Đáp án cân không hợp lệ"
        identified = answer.get("identified_coin")
        weighings = answer.get("weighings") or []
        try:
            identified = int(identified)
        except Exception:
            return None, "Chưa chọn đồng xu"
        light = int(doc.get("light_coin_index"))
        if len(weighings) > int(ch.get("max_weighings") or 2):
            return None, "Vượt quá 2 lần cân"
        # Validate weighings consistency (optional light simulation)
        for w in weighings:
            left = [int(x) for x in (w.get("left") or [])]
            right = [int(x) for x in (w.get("right") or [])]
            if not left or not right or len(left) != len(right):
                return None, "Mỗi lần cân cần hai đĩa cùng số đồng"
        is_correct = identified == light and 0 <= identified <= 8
        points = int(ch["points"]) if is_correct else 0
        detail = ch["explanation"] if is_correct else f"Đồng nhẹ là #{light + 1}."
        expected = light
    else:
        ans = answer
        if isinstance(answer, dict):
            ans = answer.get("option_id") or answer.get("choice") or answer.get("id")
        ans = str(ans).strip()
        is_correct = ans == str(expected)
        points = int(ch["points"]) if is_correct else 0
        detail = ch["explanation"]

    # Speed bonus nhỏ (tối đa +2, không đẩy vượt cấu trúc quá nhiều) — giới hạn tổng phụ
    bonus = 0
    try:
        ms = int(reaction_ms) if reaction_ms is not None else None
    except Exception:
        ms = None
    if is_correct and ms is not None and ms > 0:
        if ms < 8000:
            bonus = 2
        elif ms < 15000:
            bonus = 1
    points_awarded = points + bonus

    answers = dict(doc.get("answers") or {})
    answers[key] = {
        "raw": answer,
        "normalized": ans if ch["kind"] != "balance" else identified,
        "is_correct": is_correct,
        "points": points_awarded,
        "base_points": points,
        "bonus": bonus,
        "reaction_ms": ms,
        "at": _now(),
    }
    per = list(doc.get("per_question") or [])
    per.append({
        "question_id": question_id,
        "slug": ch["slug"],
        "title": ch["title"],
        "is_correct": is_correct,
        "points": points_awarded,
        "student_answer": answers[key]["normalized"],
        "correct_answer": expected if ch["kind"] != "balance" else int(doc.get("light_coin_index")),
        "explanation": ch["explanation"],
        "reaction_ms": ms,
    })

    raw_total = sum(int(a.get("points") or 0) for a in answers.values())
    total = min(150, raw_total)  # điểm gốc tối đa 150; thưởng tốc độ không vượt trần
    correct_count = sum(1 for a in answers.values() if a.get("is_correct"))
    next_idx = question_id + 1
    finished = len(answers) >= len(CHALLENGES)

    updates = {
        "answers": answers,
        "per_question": per,
        "total_score": total,
        "correct_count": correct_count,
        "current_index": min(next_idx, len(CHALLENGES)),
        "updated_at": _now(),
    }
    if finished:
        updates["status"] = "finished"
        updates["submitted"] = True
        updates["finished_at"] = _now()
        started = doc.get("started_at")
        if isinstance(started, datetime):
            updates["duration_sec"] = max(0, int((updates["finished_at"] - started).total_seconds()))

    col(COLL).update_one({"_id": doc["_id"]}, {"$set": updates})
    doc = get_attempt(attempt_id)

    result = {
        "is_correct": is_correct,
        "points": points_awarded,
        "bonus": bonus,
        "explanation": detail,
        "total_score": total,
        "correct_count": correct_count,
        "finished": finished,
        "attempt": public_attempt(doc, include_review=finished),
    }
    if ch["kind"] == "balance":
        result["light_coin_index"] = int(doc.get("light_coin_index"))
    else:
        result["correct_answer"] = expected
    return result, None


def simulate_weigh(attempt_id: str, left: list, right: list):
    """Trả về nghiêng cân mà không tiết lộ index (chỉ outcome)."""
    doc = get_attempt(attempt_id)
    if not doc or doc.get("status") != "in_progress":
        return None, "Phiên không hợp lệ"
    light = int(doc.get("light_coin_index"))
    try:
        L = [int(x) for x in left]
        R = [int(x) for x in right]
    except Exception:
        return None, "Danh sách đồng không hợp lệ"
    if not L or not R or len(L) != len(R):
        return None, "Hai đĩa phải cùng số đồng xu"
    if set(L) & set(R):
        return None, "Không đặt một đồng lên cả hai đĩa"
    for i in L + R:
        if i < 0 or i > 8:
            return None, "Chỉ số đồng 0–8"

    def side_weight(side):
        # Đồng nhẹ = 9, còn lại = 10
        return sum(9 if i == light else 10 for i in side)

    wl, wr = side_weight(L), side_weight(R)
    if wl < wr:
        outcome = "left"
    elif wl > wr:
        outcome = "right"
    else:
        outcome = "balance"
    return {"outcome": outcome}, None


def list_attempts(grade=None, limit=100):
    q = {}
    if grade in ("6", "7"):
        q["grade"] = grade
    docs = list(col(COLL).find(q).sort("finished_at", -1).limit(limit))
    rows = []
    for d in docs:
        rows.append({
            "id": str(d["_id"]),
            "full_name": d.get("full_name"),
            "class_name": d.get("class_name"),
            "grade": d.get("grade"),
            "status": d.get("status"),
            "total_score": d.get("total_score"),
            "correct_count": d.get("correct_count"),
            "duration_sec": d.get("duration_sec"),
            "rank_title": rank_title(d.get("total_score") or 0),
            "started_at": _iso(d.get("started_at")),
            "finished_at": _iso(d.get("finished_at")),
        })
    return rows


def attempt_detail_admin(attempt_id: str):
    doc = get_attempt(attempt_id)
    if not doc:
        return None
    data = public_attempt(doc, include_review=True)
    data["per_question"] = doc.get("per_question") or []
    data["answers"] = doc.get("answers") or {}
    return data


def leaderboard(grade=None, limit=20):
    q = {"status": "finished"}
    if grade in ("6", "7"):
        q["grade"] = grade
    docs = list(
        col(COLL)
        .find(q)
        .sort([("total_score", -1), ("duration_sec", 1)])
        .limit(limit)
    )
    return [
        {
            "full_name": d.get("full_name"),
            "class_name": d.get("class_name"),
            "grade": d.get("grade"),
            "total_score": d.get("total_score"),
            "duration_sec": d.get("duration_sec"),
            "rank_title": rank_title(d.get("total_score") or 0),
        }
        for d in docs
    ]
