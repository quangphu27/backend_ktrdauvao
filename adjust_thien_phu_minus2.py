"""Trần Lê Thiên Phú: giảm 2 câu đúng."""
from __future__ import annotations

import os
import sys
from copy import deepcopy

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
QUIZ_ID = "6ab7e539c4110429822a0cb0"


def norm(s: str) -> str:
    return " ".join((s or "").strip().lower().split())


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    db = MongoClient(os.getenv("MONGODB_URI"))[os.getenv("MONGODB_DB_NAME")]
    quiz = db.quizzes.find_one({"_id": ObjectId(QUIZ_ID)})
    qmap = {
        str(q.get("id")): q
        for q in (quiz.get("questions") or [])
        if q.get("type") == "mcq"
    }

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

    a = next(
        x
        for x in db.quiz_attempts.find({"quiz_id": QUIZ_ID})
        if norm(x.get("student_name")) == norm("Trần Lê Thiên Phú")
    )
    details = deepcopy(a.get("details") or [])
    mc_i = [i for i, d in enumerate(details) if d.get("type") == "mcq"]
    before = sum(1 for i in mc_i if details[i].get("is_correct"))
    rights = [i for i in mc_i if details[i].get("is_correct")]
    for i in rights[-2:]:
        d = details[i]
        q = qmap.get(str(d.get("question_id"))) or {}
        correct = d.get("correct_answer") or correct_text(q)
        wrong = wrong_text(q)
        if wrong == correct:
            wrong = "(trống)"
        d["student_answer"] = wrong or "(trống)"
        d["correct_answer"] = correct
        d["is_correct"] = False
        d["points_awarded"] = 0
        d["answered"] = True

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
    after = sum(1 for i in mc_i if details[i].get("is_correct"))

    db.quiz_attempts.update_one(
        {"_id": a["_id"]},
        {
            "$set": {
                "details": details,
                "earned": earned,
                "max_score": max_score,
                "score": score,
                "pending_manual": pending,
            }
        },
    )
    tn = round(after / 30 * 100, 1)
    print(f"Trần Lê Thiên Phú: {before} -> {after}/30 | score {a.get('score')} -> {score} | TN={tn}/100")


if __name__ == "__main__":
    main()
