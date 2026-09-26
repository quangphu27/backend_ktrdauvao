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
    if qtype not in ("mcq", "text", "python_code", "scratch_file"):
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
        q["explanation"] = (raw.get("explanation") or "").strip() or None
        q["correct_answer"] = None
        q["starter_code"] = ""
        q["allow_run"] = False
    elif qtype == "text":
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
        q["starter_code"] = ""
        q["allow_run"] = False
    elif qtype == "scratch_file":
        # Nộp file .sb3 — giáo viên chấm thủ công, xem trên web
        q["options"] = []
        q["correct_answer"] = None
        q["answer_aliases"] = []
        q["starter_code"] = ""
        q["allow_run"] = False
        q["hint"] = (raw.get("hint") or "").strip() or None
        accept = raw.get("accept_extensions") or [".sb3"]
        if isinstance(accept, str):
            accept = [accept]
        q["accept_extensions"] = [
            (a if str(a).startswith(".") else f".{a}").lower()
            for a in accept
            if a
        ] or [".sb3"]
    else:
        # python_code — tự luận viết code; có testcases thì chấm tự động
        starter = raw.get("starter_code")
        if starter is None:
            starter = ""
        q["options"] = []
        q["correct_answer"] = (raw.get("correct_answer") or "").strip() or None
        q["answer_aliases"] = []
        q["starter_code"] = str(starter)
        q["allow_run"] = bool(raw.get("allow_run", True))
        q["hint"] = (raw.get("hint") or "").strip() or None
        # File mẫu (hiển thị + ghi vào môi trường chạy thử)
        sample_files = []
        for sf in raw.get("sample_files") or []:
            name = (sf.get("name") or "").strip()
            if not name:
                continue
            sample_files.append({
                "name": name,
                "content": str(sf.get("content") if sf.get("content") is not None else ""),
            })
        q["sample_files"] = sample_files
        q["testcases"] = _sanitize_testcases(raw.get("testcases") or [], index)
        q["function_name"] = (raw.get("function_name") or "").strip() or None
    return q


def _sanitize_testcases(raw_list, q_index=0):
    """Chuẩn hóa testcase cho câu python_code.

    mode=function: gọi hàm với args, so sánh return
    mode=stdin: giả lập input(), so sánh stdout
    mode=class_method: tạo object class rồi gọi method, so sánh return
    """
    out = []
    for i, tc in enumerate(raw_list or []):
        if not isinstance(tc, dict):
            continue
        mode = (tc.get("mode") or "stdin").lower()
        if mode not in ("function", "stdin", "class_method"):
            mode = "stdin"
        item = {
            "id": tc.get("id") or new_id(),
            "name": (tc.get("name") or f"Test {i + 1}").strip(),
            "mode": mode,
        }
        if mode == "function":
            item["function_name"] = (tc.get("function_name") or "").strip()
            item["args"] = tc.get("args") if isinstance(tc.get("args"), list) else []
            item["expected"] = tc.get("expected")
        elif mode == "class_method":
            item["class_name"] = (tc.get("class_name") or "").strip()
            item["constructor_args"] = (
                tc.get("constructor_args") if isinstance(tc.get("constructor_args"), list) else []
            )
            item["method"] = (tc.get("method") or "").strip()
            item["method_args"] = tc.get("method_args") if isinstance(tc.get("method_args"), list) else []
            item["expected"] = tc.get("expected")
        else:
            stdin = tc.get("stdin")
            if stdin is None:
                stdin = ""
            item["stdin"] = str(stdin)
            item["expected_stdout"] = str(tc.get("expected_stdout") if tc.get("expected_stdout") is not None else "")
        out.append(item)
    return out


def sanitize_questions(raw_list):
    out = []
    for i, raw in enumerate(raw_list or []):
        out.append(sanitize_question(raw, i))
    if not out:
        raise ValueError("Bài kiểm tra cần ít nhất 1 câu hỏi")
    return out


def question_for_student(q, include_explanation=False):
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
        if include_explanation and q.get("explanation"):
            item["explanation"] = q["explanation"]
    elif item["type"] == "python_code":
        item["starter_code"] = q.get("starter_code") or ""
        item["allow_run"] = bool(q.get("allow_run", True))
        item["hint"] = q.get("hint")
        item["sample_files"] = q.get("sample_files") or []
        item["function_name"] = q.get("function_name")
        # Gửi testcases cho client chạy Pyodide khi nộp bài
        item["testcases"] = q.get("testcases") or []
        item["has_testcases"] = bool(q.get("testcases"))
    elif item["type"] == "scratch_file":
        item["hint"] = q.get("hint")
        item["accept_extensions"] = q.get("accept_extensions") or [".sb3"]
    return item


def quiz_to_dict(doc, include_answers=False, include_explanations=False):
    if not doc:
        return None
    questions = doc.get("questions") or []
    if include_answers:
        qs = questions
    else:
        qs = [
            question_for_student(q, include_explanation=include_explanations)
            for q in questions
        ]

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


def _extract_code_answer(student_ans):
    """answers có thể là string code hoặc {code, test_result}."""
    if student_ans is None:
        return "", None
    if isinstance(student_ans, dict):
        code = student_ans.get("code")
        if code is None:
            code = student_ans.get("answer") or ""
        return str(code), student_ans.get("test_result")
    return str(student_ans), None


def _extract_file_answer(student_ans):
    """answers scratch_file: {url, original_name, ...}."""
    if not isinstance(student_ans, dict):
        return None
    url = (student_ans.get("url") or "").strip()
    if not url:
        return None
    return {
        "url": url,
        "original_name": student_ans.get("original_name") or "",
        "public_id": student_ans.get("public_id") or "",
        "resource_type": student_ans.get("resource_type") or "raw",
        "format": student_ans.get("format") or "",
        "bytes": student_ans.get("bytes") or 0,
    }


def grade_attempt(quiz, answers_map, code_grades=None):
    """Chấm bài. answers_map: {question_id: option_id | text | code | {code, test_result} | file meta}.

    code_grades (optional): {question_id: {passed, total, results}} — kết quả testcase từ client.
    """
    answers_map = answers_map or {}
    code_grades = code_grades or {}
    details = []
    earned = 0
    max_score = 0
    pending_manual = 0

    for q in quiz.get("questions") or []:
        points = int(q.get("points") or 1)
        max_score += points
        qid = str(q["id"])
        student_ans = answers_map.get(qid)
        if student_ans is None:
            student_ans = answers_map.get(q["id"])

        qtype = q.get("type") or "mcq"
        is_correct = False
        chosen_text = ""
        correct_text = ""
        needs_manual_review = False
        points_awarded = 0

        if qtype == "scratch_file":
            file_meta = _extract_file_answer(student_ans)
            answered = bool(file_meta)
            needs_manual_review = True
            is_correct = None
            correct_text = "(Giáo viên chấm thủ công — xem file Scratch)"
            chosen_text = (file_meta or {}).get("original_name") or ((file_meta or {}).get("url") or "")
            if answered:
                pending_manual += 1
            details.append({
                "question_id": qid,
                "type": qtype,
                "content": q.get("content"),
                "image_url": q.get("image_url"),
                "points": points,
                "points_awarded": 0,
                "student_answer": chosen_text,
                "file": file_meta,
                "correct_answer": correct_text,
                "is_correct": is_correct,
                "answered": answered,
                "needs_manual_review": needs_manual_review,
            })
            continue

        if qtype == "python_code":
            chosen_text, embedded = _extract_code_answer(student_ans)
            answered = bool(chosen_text.strip())
            testcases = q.get("testcases") or []
            grade_info = code_grades.get(qid) or code_grades.get(q["id"]) or embedded or {}
            if not isinstance(grade_info, dict):
                grade_info = {}

            if testcases:
                total = len(testcases)
                passed = int(grade_info.get("passed") or 0)
                passed = max(0, min(passed, total))
                if total > 0 and answered and passed >= total:
                    is_correct = True
                    points_awarded = points
                    earned += points
                elif answered and total > 0 and passed > 0:
                    is_correct = False
                    points_awarded = int(round(points * passed / total))
                    earned += points_awarded
                else:
                    is_correct = False if answered else False
                    points_awarded = 0
                needs_manual_review = False
                correct_text = f"Testcase: {passed}/{total} đạt"
                details.append({
                    "question_id": qid,
                    "type": qtype,
                    "content": q.get("content"),
                    "image_url": q.get("image_url"),
                    "points": points,
                    "points_awarded": points_awarded,
                    "student_answer": chosen_text,
                    "correct_answer": correct_text,
                    "is_correct": is_correct if answered else False,
                    "answered": answered,
                    "needs_manual_review": False,
                    "tests_passed": passed,
                    "tests_total": total,
                    "test_results": grade_info.get("results") or [],
                })
            else:
                needs_manual_review = True
                is_correct = None  # chưa chấm
                correct_text = q.get("correct_answer") or "(Giáo viên chấm thủ công)"
                if answered:
                    pending_manual += 1
                details.append({
                    "question_id": qid,
                    "type": qtype,
                    "content": q.get("content"),
                    "image_url": q.get("image_url"),
                    "points": points,
                    "points_awarded": 0,
                    "student_answer": chosen_text,
                    "correct_answer": correct_text,
                    "is_correct": is_correct,
                    "answered": answered,
                    "needs_manual_review": needs_manual_review,
                })
            continue

        if qtype == "text":
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
            points_awarded = points

        answered_flag = False
        if student_ans is not None:
            if isinstance(student_ans, dict):
                answered_flag = bool(str(student_ans.get("code") or "").strip())
            else:
                answered_flag = bool(str(student_ans).strip())

        details.append({
            "question_id": qid,
            "type": qtype,
            "content": q.get("content"),
            "image_url": q.get("image_url"),
            "points": points,
            "points_awarded": points_awarded,
            "student_answer": chosen_text,
            "correct_answer": correct_text,
            "is_correct": is_correct,
            "answered": answered_flag,
            "needs_manual_review": False,
        })

    score = round((earned / max_score) * 100, 1) if max_score else 0
    return {
        "earned": earned,
        "max_score": max_score,
        "score": score,
        "details": details,
        "pending_manual": pending_manual,
    }


def recompute_attempt_score(details):
    """Tính lại điểm sau khi giáo viên chấm code."""
    earned = 0
    max_score = 0
    pending = 0
    for d in details or []:
        pts = int(d.get("points") or 0)
        max_score += pts
        if d.get("needs_manual_review") and d.get("is_correct") is None:
            pending += 1 if d.get("answered") else 0
            awarded = int(d.get("points_awarded") or 0)
        else:
            awarded = int(d.get("points_awarded") or 0)
            if d.get("is_correct") is True and awarded == 0:
                awarded = pts
        earned += awarded
    score = round((earned / max_score) * 100, 1) if max_score else 0
    return earned, max_score, score, pending


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
        "pending_manual": doc.get("pending_manual") or 0,
        "duration_seconds": doc.get("duration_seconds") or 0,
        "submitted_at": submitted.isoformat() + "Z" if isinstance(submitted, datetime) else submitted,
    }
    if include_details:
        data["details"] = doc.get("details") or []
        data["answers"] = doc.get("answers") or {}
    return data
