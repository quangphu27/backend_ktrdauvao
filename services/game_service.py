"""Helpers trò chơi ô chữ bí mật & games hub."""

from __future__ import annotations

import re
import secrets
import uuid
from datetime import datetime


def new_id():
    return str(uuid.uuid4())


def generate_slug(length=8):
    return secrets.token_urlsafe(length)[:length].lower().replace("_", "x").replace("-", "y")


def _norm_answer(s):
    s = (s or "").strip().upper()
    s = re.sub(r"\s+", "", s)
    # bỏ dấu tiếng Việt đơn giản khi so khớp ô chữ (giữ nguyên chữ cái)
    return s


def _strip_accents(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.replace("Đ", "D").replace("đ", "d")


def normalize_letters(answer):
    """Chuỗi chữ cái cho lưới (hoa, không khoảng trắng, bỏ dấu)."""
    s = _strip_accents((answer or "").strip().upper())
    s = re.sub(r"[^A-Z0-9]", "", s)
    return s


def sanitize_mcq_question(raw, label="Câu hỏi"):
    content = (raw.get("content") or "").strip()
    image_url = (raw.get("image_url") or "").strip() or None
    if not content and not image_url:
        raise ValueError(f"{label}: cần nội dung hoặc ảnh")
    options = []
    for opt in raw.get("options") or []:
        text = (opt.get("text") or "").strip()
        if not text:
            continue
        options.append({
            "id": opt.get("id") or new_id(),
            "text": text,
            "is_correct": bool(opt.get("is_correct")),
        })
    if len(options) != 4:
        raise ValueError(f"{label}: cần đúng 4 đáp án")
    if sum(1 for o in options if o["is_correct"]) != 1:
        raise ValueError(f"{label}: cần đúng 1 đáp án đúng")
    return {
        "content": content,
        "image_url": image_url,
        "options": options,
    }


def sanitize_crossword_row(raw, index=0):
    answer_display = (raw.get("answer") or "").strip().upper()
    letters = normalize_letters(raw.get("answer") or "")
    if len(letters) < 2:
        raise ValueError(f"Hàng {index + 1}: đáp án cần ít nhất 2 ký tự")
    try:
        key_index = int(raw.get("key_index", 0))
    except (TypeError, ValueError):
        key_index = 0
    if key_index < 0 or key_index >= len(letters):
        raise ValueError(f"Hàng {index + 1}: vị trí chữ dọc không hợp lệ (0–{len(letters) - 1})")
    q = sanitize_mcq_question(raw.get("question") or {}, f"Hàng ngang {index + 1}")
    return {
        "id": raw.get("id") or new_id(),
        "number": index + 1,
        "answer": letters,
        "answer_display": answer_display or letters,
        "key_index": key_index,
        "points": 10,
        "question": q,
    }


def sanitize_crossword_payload(data):
    title = (data.get("title") or "").strip()
    if not title:
        raise ValueError("Vui lòng nhập tên trò chơi")
    rows_raw = data.get("rows") or []
    if len(rows_raw) < 2:
        raise ValueError("Cần ít nhất 2 hàng ngang")
    if len(rows_raw) > 12:
        raise ValueError("Tối đa 12 hàng ngang")
    rows = [sanitize_crossword_row(r, i) for i, r in enumerate(rows_raw)]
    vertical_letters = "".join(r["answer"][r["key_index"]] for r in rows)
    vertical_answer = normalize_letters(data.get("vertical_answer") or vertical_letters)
    if vertical_answer and vertical_answer != vertical_letters:
        # Cho phép admin nhập từ dọc; kiểm tra khớp với key_index
        if len(vertical_answer) != len(rows):
            raise ValueError("Từ hàng dọc phải bằng số hàng ngang")
        for i, row in enumerate(rows):
            if row["answer"][row["key_index"]] != vertical_answer[i]:
                raise ValueError(
                    f"Hàng {i + 1}: chữ tại vị trí dọc phải là «{vertical_answer[i]}» "
                    f"(đang là «{row['answer'][row['key_index']]}»)"
                )
    else:
        vertical_answer = vertical_letters

    vertical_q = sanitize_mcq_question(
        data.get("vertical_question") or {},
        "Câu hỏi hàng dọc",
    )
    return {
        "title": title,
        "description": (data.get("description") or "").strip(),
        "rows": rows,
        "vertical_answer": vertical_answer,
        "vertical_question": vertical_q,
        "vertical_points": 30,
        "is_active": bool(data.get("is_active", True)),
    }


def crossword_to_dict(doc, include_answers=False):
    if not doc:
        return None
    created = doc.get("created_at")
    rows = []
    for r in doc.get("rows") or []:
        item = {
            "id": r["id"],
            "number": r.get("number"),
            "length": len(r.get("answer") or ""),
            "key_index": r.get("key_index", 0),
            "points": r.get("points", 10),
            "question": {
                "content": (r.get("question") or {}).get("content"),
                "image_url": (r.get("question") or {}).get("image_url"),
                "options": [
                    {"id": o["id"], "text": o["text"]}
                    for o in ((r.get("question") or {}).get("options") or [])
                ],
            },
        }
        if include_answers:
            item["answer"] = r.get("answer")
            item["answer_display"] = r.get("answer_display")
            item["question"]["options"] = (r.get("question") or {}).get("options") or []
        rows.append(item)

    vq = doc.get("vertical_question") or {}
    vertical_question = {
        "content": vq.get("content"),
        "image_url": vq.get("image_url"),
        "options": [
            {"id": o["id"], "text": o["text"]}
            for o in (vq.get("options") or [])
        ],
    }
    if include_answers:
        vertical_question["options"] = vq.get("options") or []

    data = {
        "id": str(doc["_id"]),
        "type": "crossword",
        "title": doc.get("title"),
        "description": doc.get("description") or "",
        "slug": doc.get("slug"),
        "is_active": bool(doc.get("is_active", True)),
        "rows": rows,
        "vertical_points": doc.get("vertical_points", 30),
        "vertical_question": vertical_question,
        "players": doc.get("players") or [],
        "solved_rows": doc.get("solved_rows") or [],
        "vertical_solved": bool(doc.get("vertical_solved")),
        "created_at": created.isoformat() + "Z" if isinstance(created, datetime) else created,
        "play_path": f"/tro-choi/o-chu/{doc.get('slug')}",
    }
    if include_answers:
        data["vertical_answer"] = doc.get("vertical_answer")
        # Reveal solved answers for play board sync
        data["row_answers"] = {
            r["id"]: r.get("answer") for r in (doc.get("rows") or [])
        }
    return data


def check_option_correct(question, option_id):
    for o in (question or {}).get("options") or []:
        if str(o.get("id")) == str(option_id):
            return bool(o.get("is_correct")), o.get("text") or ""
    return False, ""


# ── Fast quiz (Ai nhanh hơn) ────────────────────────────

def sanitize_fast_quiz(data):
    title = (data.get("title") or "").strip()
    if not title:
        raise ValueError("Vui lòng nhập tên trò chơi")
    questions = []
    for i, raw in enumerate(data.get("questions") or []):
        q = sanitize_mcq_question(raw, f"Câu {i + 1}")
        questions.append({
            "id": raw.get("id") or new_id(),
            "points": max(5, int(raw.get("points") or 10)),
            **q,
        })
    if len(questions) < 1:
        raise ValueError("Cần ít nhất 1 câu hỏi")
    return {
        "title": title,
        "description": (data.get("description") or "").strip(),
        "questions": questions,
        "is_active": bool(data.get("is_active", True)),
    }


def fast_quiz_to_dict(doc, include_answers=False):
    if not doc:
        return None
    qs = []
    for q in doc.get("questions") or []:
        item = {
            "id": q["id"],
            "content": q.get("content"),
            "image_url": q.get("image_url"),
            "points": q.get("points", 10),
            "options": [
                {"id": o["id"], "text": o["text"]}
                for o in (q.get("options") or [])
            ],
        }
        if include_answers:
            item["options"] = q.get("options") or []
        qs.append(item)
    created = doc.get("created_at")
    return {
        "id": str(doc["_id"]),
        "type": "fast_quiz",
        "title": doc.get("title"),
        "description": doc.get("description") or "",
        "slug": doc.get("slug"),
        "is_active": bool(doc.get("is_active", True)),
        "questions": qs,
        "players": doc.get("players") or [],
        "created_at": created.isoformat() + "Z" if isinstance(created, datetime) else created,
        "play_path": f"/tro-choi/nhanh/{doc.get('slug')}",
    }


# ── Picture word (Đuổi hình bắt chữ) ────────────────────

def sanitize_picture_word(data):
    title = (data.get("title") or "").strip()
    if not title:
        raise ValueError("Vui lòng nhập tên trò chơi")
    rounds = []
    for i, raw in enumerate(data.get("rounds") or []):
        answer = normalize_letters(raw.get("answer") or "")
        if len(answer) < 2:
            raise ValueError(f"Vòng {i + 1}: đáp án cần ≥ 2 ký tự")
        image_url = (raw.get("image_url") or "").strip()
        if not image_url:
            raise ValueError(f"Vòng {i + 1}: cần ảnh gợi ý")
        hint = (raw.get("hint") or "").strip()
        rounds.append({
            "id": raw.get("id") or new_id(),
            "image_url": image_url,
            "hint": hint,
            "answer": answer,
            "points": max(5, int(raw.get("points") or 10)),
        })
    if not rounds:
        raise ValueError("Cần ít nhất 1 vòng chơi")
    return {
        "title": title,
        "description": (data.get("description") or "").strip(),
        "rounds": rounds,
        "is_active": bool(data.get("is_active", True)),
    }


def picture_word_to_dict(doc, include_answers=False):
    if not doc:
        return None
    rounds = []
    for r in doc.get("rounds") or []:
        item = {
            "id": r["id"],
            "image_url": r.get("image_url"),
            "hint": r.get("hint") or "",
            "length": len(r.get("answer") or ""),
            "points": r.get("points", 10),
        }
        if include_answers:
            item["answer"] = r.get("answer")
        rounds.append(item)
    created = doc.get("created_at")
    return {
        "id": str(doc["_id"]),
        "type": "picture_word",
        "title": doc.get("title"),
        "description": doc.get("description") or "",
        "slug": doc.get("slug"),
        "is_active": bool(doc.get("is_active", True)),
        "rounds": rounds,
        "players": doc.get("players") or [],
        "created_at": created.isoformat() + "Z" if isinstance(created, datetime) else created,
        "play_path": f"/tro-choi/hinh-chu/{doc.get('slug')}",
    }
