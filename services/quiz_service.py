"""Helpers cho bài kiểm tra tự tạo (quiz)."""

from __future__ import annotations

import re
import secrets
import uuid
from datetime import datetime


def generate_quiz_slug(length=8):
    return secrets.token_urlsafe(length)[:length].lower().replace("_", "x").replace("-", "y")


def new_id():
    return str(uuid.uuid4())


def _norm_text(s):
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def sanitize_question(raw, index=0):
    """Chuẩn hóa 1 câu hỏi từ payload admin."""
    qtype = (raw.get("type") or "mcq").lower()
    if qtype not in ("mcq", "text"):
        qtype = "mcq"

    q = {
        "id": raw.get("id") or new_id(),
        "type": qtype,
        "content": (raw.get("content") or "").strip(),
        "image_url": (raw.get("image_url") or "").strip() or None,
        "points": max(1, int(raw.get("points") or 1)),
        "order_num": int(raw.get("order_num") if raw.get("order_num") is not None else index),
    }
    if not q["content"] and not q["image_url"]:
        raise ValueError(f"Câu {index + 1}: cần nội dung hoặc ảnh")

    if qtype == "mcq":
        options = []
        for opt in raw.get("options") or []:
            text = (opt.get("text") or opt.get("answer_text") or "").strip()
            if not text:
                continue
            options.append({
                "id": opt.get("id") or new_id(),
                "text": text,
                "is_correct": bool(opt.get("is_correct")),
            })
        if len(options) < 2:
            raise ValueError(f"Câu {index + 1}: trắc nghiệm cần ít nhất 2 đáp án")
        if not any(o["is_correct"] for o in options):
            raise ValueError(f"Câu {index + 1}: cần chọn 1 đáp án đúng")
        q["options"] = options
        q["correct_answer"] = None
    else:
        correct = (raw.get("correct_answer") or "").strip()
        if not correct:
            raise ValueError(f"Câu {index + 1}: tự luận cần đáp án đúng để chấm")
        aliases = [
            a.strip()
            for a in (raw.get("answer_aliases") or [])
            if isinstance(a, str) and a.strip()
        ]
        q["options"] = []
        q["correct_answer"] = correct
        q["answer_aliases"] = aliases
    return q


def sanitize_questions(raw_list):
    out = []
    for i, raw in enumerate(raw_list or []):
        out.append(sanitize_question(raw, i))
    if not out:
        raise ValueError("Bài kiểm tra cần ít nhất 1 câu hỏi")
    return out


def question_for_student(q):
    """Ẩn đáp án đúng khi gửi cho học sinh."""
    item = {
        "id": q["id"],
        "type": q.get("type", "mcq"),
        "content": q.get("content"),
        "image_url": q.get("image_url"),
        "points": q.get("points", 1),
        "order_num": q.get("order_num", 0),
    }
    if item["type"] == "mcq":
        item["options"] = [
            {"id": o["id"], "text": o["text"]}
            for o in (q.get("options") or [])
        ]
    return item


def quiz_to_dict(doc, include_answers=False):
    if not doc:
        return None
    questions = doc.get("questions") or []
    if include_answers:
        qs = questions
    else:
        qs = [question_for_student(q) for q in questions]

    created = doc.get("created_at")
    updated = doc.get("updated_at")
    return {
        "id": str(doc["_id"]),
        "title": doc.get("title"),
        "description": doc.get("description") or "",
        "slug": doc.get("slug"),
        "duration_minutes": int(doc.get("duration_minutes") or 0),
        "is_active": bool(doc.get("is_active", True)),
        "question_count": len(questions),
        "max_score": sum(int(q.get("points") or 1) for q in questions),
        "questions": qs,
        "created_at": created.isoformat() + "Z" if isinstance(created, datetime) else created,
        "updated_at": updated.isoformat() + "Z" if isinstance(updated, datetime) else updated,
        "public_path": f"/quiz/{doc.get('slug')}",
    }


def grade_attempt(quiz, answers_map):
    """Chấm bài. answers_map: {question_id: option_id | text}."""
    answers_map = answers_map or {}
    details = []
    earned = 0
    max_score = 0

    for q in quiz.get("questions") or []:
        points = int(q.get("points") or 1)
        max_score += points
        qid = str(q["id"])
        student_ans = answers_map.get(qid)
        if student_ans is None:
            student_ans = answers_map.get(q["id"])

        is_correct = False
        chosen_text = ""
        correct_text = ""

        if q.get("type") == "text":
            correct_text = q.get("correct_answer") or ""
            chosen_text = "" if student_ans is None else str(student_ans)
            accepted = [_norm_text(correct_text)] + [
                _norm_text(a) for a in (q.get("answer_aliases") or [])
            ]
            is_correct = bool(chosen_text) and _norm_text(chosen_text) in accepted
        else:
            correct_opt = next((o for o in (q.get("options") or []) if o.get("is_correct")), None)
            correct_text = correct_opt["text"] if correct_opt else ""
            chosen_opt = next(
                (o for o in (q.get("options") or []) if str(o.get("id")) == str(student_ans)),
                None,
            )
            chosen_text = chosen_opt["text"] if chosen_opt else ""
            is_correct = bool(chosen_opt and chosen_opt.get("is_correct"))

        if is_correct:
            earned += points

        details.append({
            "question_id": qid,
            "type": q.get("type"),
            "content": q.get("content"),
            "image_url": q.get("image_url"),
            "points": points,
            "student_answer": chosen_text,
            "correct_answer": correct_text,
            "is_correct": is_correct,
            "answered": bool(str(student_ans).strip()) if student_ans is not None else False,
        })

    score = round((earned / max_score) * 100, 1) if max_score else 0
    return {
        "earned": earned,
        "max_score": max_score,
        "score": score,
        "details": details,
    }


def attempt_to_dict(doc, include_details=False):
    if not doc:
        return None
    submitted = doc.get("submitted_at")
    data = {
        "id": str(doc["_id"]),
        "quiz_id": doc.get("quiz_id"),
        "quiz_title": doc.get("quiz_title"),
        "quiz_slug": doc.get("quiz_slug"),
        "student_name": doc.get("student_name"),
        "student_grade": doc.get("student_grade"),
        "student_phone": doc.get("student_phone") or "",
        "score": doc.get("score"),
        "earned": doc.get("earned"),
        "max_score": doc.get("max_score"),
        "duration_seconds": doc.get("duration_seconds") or 0,
        "submitted_at": submitted.isoformat() + "Z" if isinstance(submitted, datetime) else submitted,
    }
    if include_details:
        data["details"] = doc.get("details") or []
        data["answers"] = doc.get("answers") or {}
    return data
