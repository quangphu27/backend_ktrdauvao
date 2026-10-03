"""Điều chỉnh điểm TN Scratch 3 theo yêu cầu giáo viên."""
from __future__ import annotations

import os
import sys
from copy import deepcopy

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

QUIZ_ID = "6ab7e539c4110429822a0cb0"

OPS = [
    ("Trần Quang Phú", -4),
    ("Trần Lê Thiên Phú", -7),
    ("Lê Hà Linh", 6),
]


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


def rebuild(details):
    earned = max_score = pending = 0
    for d in details:
        pts = int(d.get("points") or 0)
        max_score += pts
        earned += int(d.get("points_awarded") or 0)
        if d.get("type") == "scratch_file" and (
            d.get("needs_manual_review") or d.get("is_correct") is None
        ):
            pending += 1
    score = round((earned / max_score) * 100, 1) if max_score else 0
    return earned, max_score, score, pending


def mc_ok(details):
    mc = [d for d in details if d.get("type") == "mcq"]
    return sum(1 for d in mc if d.get("is_correct")), len(mc)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    db = MongoClient(os.getenv("MONGODB_URI"))[os.getenv("MONGODB_DB_NAME")]
    quiz = db.quizzes.find_one({"_id": ObjectId(QUIZ_ID)})
    mcqs = [q for q in (quiz.get("questions") or []) if q.get("type") == "mcq"]
    qmap = {str(q.get("id")): q for q in mcqs}

    def set_correct(d, yes):
        q = qmap.get(str(d.get("question_id"))) or {}
        correct = d.get("correct_answer") or correct_text(q)
        pts = int(d.get("points") or 2)
        if yes:
            d["student_answer"] = correct
            d["is_correct"] = True
            d["points_awarded"] = pts
        else:
            wrong = wrong_text(q)
            if wrong == correct:
                wrong = "(trống)"
            d["student_answer"] = wrong or "(trống)"
            d["is_correct"] = False
            d["points_awarded"] = 0
        d["correct_answer"] = correct
        d["answered"] = True
        d["needs_manual_review"] = False

    attempts = list(db.quiz_attempts.find({"quiz_id": QUIZ_ID}))
    for name, delta in OPS:
        a = next((x for x in attempts if norm(x.get("student_name")) == norm(name)), None)
        if not a:
            print("MISSING", name)
            continue
        details = deepcopy(a.get("details") or [])
        mc_i = [i for i, d in enumerate(details) if d.get("type") == "mcq"]
        before, total = mc_ok(details)
        if delta > 0:
            wrong = [i for i in mc_i if not details[i].get("is_correct")]
            for i in wrong[:delta]:
                set_correct(details[i], True)
        elif delta < 0:
            rights = [i for i in mc_i if details[i].get("is_correct")]
            for i in rights[delta:]:
                set_correct(details[i], False)
        earned, max_score, score, pending = rebuild(details)
        after, _ = mc_ok(details)
        db.quiz_attempts.update_one(
            {"_id": a["_id"]},
            {
                "$set": {
                    "details": details,
                    "earned": earned,
                    "max_score": max_score,
                    "score": score,
                    "pending_manual": pending,
                    "student_grade": "Scratch3",
                }
            },
        )
        print(
            f"{name}: {before} -> {after}/{total} | score {a.get('score')} -> {score} | delta={delta}"
        )


if __name__ == "__main__":
    main()
