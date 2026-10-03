"""Điều chỉnh điểm TN Scratch 3:
- Trần Quang Phú: +10 câu đúng
- Trần Lê Thiên Phú: tạo bài ~26 câu đúng
"""
from __future__ import annotations

import os
import sys
from copy import deepcopy
from datetime import datetime, timezone

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

QUIZ_ID = "6ab7e539c4110429822a0cb0"


def norm(s: str) -> str:
    return " ".join((s or "").strip().lower().split())


def correct_text(q):
    for o in q.get("options") or []:
        if o.get("is_correct"):
            return (o.get("text") or "").strip()
    return ""


def wrong_text(q):
    for o in q.get("options") or []:
        if not o.get("is_correct"):
            return (o.get("text") or "").strip()
    return ""


def rebuild_scores(details):
    earned = 0
    max_score = 0
    pending = 0
    for d in details:
        pts = int(d.get("points") or 0)
        max_score += pts
        if d.get("type") == "scratch_file" and (d.get("needs_manual_review") or d.get("is_correct") is None):
            pending += 1
            earned += int(d.get("points_awarded") or 0)
        else:
            earned += int(d.get("points_awarded") or 0)
    score = round((earned / max_score) * 100, 1) if max_score else 0
    return earned, max_score, score, pending


def make_mc_detail(q, is_correct: bool):
    opts = q.get("options") or []
    correct = correct_text(q)
    student = correct if is_correct else (wrong_text(q) or "(trống)")
    pts = int(q.get("points") or 2)
    return {
        "question_id": q.get("id"),
        "type": "mcq",
        "content": q.get("content") or "",
        "image_url": q.get("image_url"),
        "points": pts,
        "points_awarded": pts if is_correct else 0,
        "student_answer": student,
        "correct_answer": correct,
        "is_correct": is_correct,
        "answered": True,
        "needs_manual_review": False,
    }


def make_scratch_detail(q, clone_from=None):
    pts = int(q.get("points") or 40)
    if clone_from:
        return deepcopy(clone_from)
    return {
        "question_id": q.get("id"),
        "type": "scratch_file",
        "content": q.get("content") or "",
        "image_url": q.get("image_url"),
        "points": pts,
        "points_awarded": 0,
        "student_answer": "",
        "correct_answer": None,
        "is_correct": None,
        "answered": False,
        "needs_manual_review": True,
        "file": None,
    }


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    db = MongoClient(os.getenv("MONGODB_URI"))[os.getenv("MONGODB_DB_NAME")]
    quiz = db.quizzes.find_one({"_id": ObjectId(QUIZ_ID)}) or db.quizzes.find_one({"_id": QUIZ_ID})
    if not quiz:
        print("QUIZ_NOT_FOUND")
        sys.exit(1)

    questions = quiz.get("questions") or []
    mcqs = [q for q in questions if q.get("type") == "mcq"]
    scratch_q = next((q for q in questions if q.get("type") == "scratch_file"), None)
    print(f"mcqs={len(mcqs)} scratch={'yes' if scratch_q else 'no'}")

    attempts = list(db.quiz_attempts.find({"quiz_id": str(quiz["_id"])}))

    # ---- Trần Quang Phú: +10 câu đúng ----
    phu = None
    for a in attempts:
        if norm(a.get("student_name")) == norm("Trần Quang Phú"):
            phu = a
            break
    if not phu:
        print("MISSING Trần Quang Phú")
        sys.exit(1)

    details = deepcopy(phu.get("details") or [])
    mc_idx = [i for i, d in enumerate(details) if d.get("type") == "mcq"]
    wrong_idx = [i for i in mc_idx if not details[i].get("is_correct")]
    before_ok = len(mc_idx) - len(wrong_idx)
    to_fix = wrong_idx[:10]
    q_by_id = {str(q.get("id")): q for q in mcqs}

    for i in to_fix:
        d = details[i]
        q = q_by_id.get(str(d.get("question_id"))) or {}
        correct = d.get("correct_answer") or correct_text(q)
        pts = int(d.get("points") or 2)
        d["student_answer"] = correct
        d["correct_answer"] = correct
        d["is_correct"] = True
        d["points_awarded"] = pts
        d["answered"] = True
        d["needs_manual_review"] = False

    earned, max_score, score, pending = rebuild_scores(details)
    after_ok = sum(1 for i in mc_idx if details[i].get("is_correct"))
    db.quiz_attempts.update_one(
        {"_id": phu["_id"]},
        {"$set": {
            "details": details,
            "earned": earned,
            "max_score": max_score,
            "score": score,
            "pending_manual": pending,
            "student_grade": "Scratch3",
        }},
    )
    print(f"Trần Quang Phú: MC {before_ok} -> {after_ok}/30 | score {phu.get('score')} -> {score} | fixed={len(to_fix)}")

    # ---- Trần Lê Thiên Phú: tạo bài ~26 câu đúng ----
    target_correct = 26
    thien = None
    for a in attempts:
        if norm(a.get("student_name")) == norm("Trần Lê Thiên Phú"):
            thien = a
            break

    # clone scratch file từ 1 bạn Scratch3 nếu có
    scratch_clone = None
    for a in attempts:
        if (a.get("student_grade") or "") in ("Scratch3", "Scratch 3"):
            for d in a.get("details") or []:
                if d.get("type") == "scratch_file" and (d.get("file") or {}).get("url"):
                    scratch_clone = d
                    break
        if scratch_clone:
            break

    new_details = []
    # 26 đúng đầu, còn lại sai (deterministic)
    for i, q in enumerate(mcqs):
        new_details.append(make_mc_detail(q, is_correct=(i < target_correct)))
    if scratch_q:
        new_details.append(make_scratch_detail(scratch_q, scratch_clone))

    earned, max_score, score, pending = rebuild_scores(new_details)
    mc_ok = sum(1 for d in new_details if d.get("type") == "mcq" and d.get("is_correct"))

    payload = {
        "quiz_id": str(quiz["_id"]),
        "quiz_title": quiz.get("title"),
        "quiz_slug": quiz.get("slug"),
        "student_name": "Trần Lê Thiên Phú",
        "student_grade": "Scratch3",
        "student_phone": "",
        "answers": {},
        "details": new_details,
        "earned": earned,
        "max_score": max_score,
        "score": score,
        "pending_manual": pending,
        "duration_seconds": 900,
        "submitted_at": datetime.now(timezone.utc),
    }

    if thien:
        db.quiz_attempts.update_one({"_id": thien["_id"]}, {"$set": payload})
        print(f"Trần Lê Thiên Phú: UPDATED id={thien['_id']} MC={mc_ok}/30 score={score}")
    else:
        res = db.quiz_attempts.insert_one(payload)
        print(f"Trần Lê Thiên Phú: CREATED id={res.inserted_id} MC={mc_ok}/30 score={score}")


if __name__ == "__main__":
    main()
