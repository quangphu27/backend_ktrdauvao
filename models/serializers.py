from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from database import col, parse_oid, oid_str


def hash_password(password):
    return generate_password_hash(password)


def verify_password(password_hash, password):
    return check_password_hash(password_hash, password)


def user_to_dict(doc):
    if not doc:
        return None
    dob = doc.get("date_of_birth")
    created = doc.get("created_at")
    return {
        "id": oid_str(doc["_id"]),
        "full_name": doc.get("full_name"),
        "email": doc.get("email"),
        "role": doc.get("role", "student"),
        "date_of_birth": dob.isoformat() if hasattr(dob, "isoformat") else dob,
        "grade": doc.get("grade"),
        "school": doc.get("school"),
        "parent_email": doc.get("parent_email"),
        "parent_phone": doc.get("parent_phone"),
        "created_at": created.isoformat() if hasattr(created, "isoformat") else created,
    }


def course_to_dict(doc):
    if not doc:
        return None
    return {
        "id": oid_str(doc["_id"]),
        "name": doc.get("name"),
        "description": doc.get("description"),
        "slug": doc.get("slug"),
    }


def question_to_dict(doc, include_correct=False):
    answers = []
    for a in doc.get("answers", []):
        aid = a.get("id") or (str(a["_id"]) if a.get("_id") else None)
        item = {
            "id": aid,
            "answer_text": a.get("answer_text"),
        }
        if include_correct:
            item["is_correct"] = bool(a.get("is_correct"))
        answers.append(item)

    return {
        "id": oid_str(doc["_id"]),
        "course_id": doc.get("course_id"),
        "content": doc.get("content"),
        "image_url": doc.get("image_url"),
        "level": doc.get("level"),
        "category": doc.get("category"),
        "order_num": doc.get("order_num", 0),
        "answers": answers,
    }


def _get_course_name(course_id):
    if not course_id:
        return None
    course = col("courses").find_one({"_id": parse_oid(course_id)})
    return course.get("name") if course else None


def _get_user(user_id):
    if not user_id:
        return None
    return col("users").find_one({"_id": parse_oid(user_id)})


def test_to_dict(doc, include_details=False):
    user = _get_user(doc.get("user_id"))
    course_name = doc.get("course_name") or _get_course_name(doc.get("course_id"))
    submitted = doc.get("submitted_at")

    data = {
        "id": oid_str(doc["_id"]),
        "user_id": doc.get("user_id"),
        "course_id": doc.get("course_id"),
        "course_name": course_name,
        "score": doc.get("score", 0),
        "radar_scores": doc.get("radar_scores", {}),
        "recommendation": doc.get("recommendation"),
        "comment": doc.get("comment"),
        "duration_seconds": doc.get("duration_seconds", 0),
        "submitted_at": submitted.isoformat() if hasattr(submitted, "isoformat") else submitted,
        "guest_name": doc.get("guest_name"),
        "guest_grade": doc.get("guest_grade"),
        "guest_phone": doc.get("guest_phone"),
        "student_name": doc.get("guest_name") or (user.get("full_name") if user else None),
        "student_grade": doc.get("guest_grade") or (user.get("grade") if user else None),
        "student_phone": doc.get("guest_phone") or (user.get("parent_phone") if user else None),
    }
    if include_details:
        data["details"] = doc.get("details", [])
    return data


def test_for_export(doc):
    """Flatten test document for Excel/PDF export."""
    user = _get_user(doc.get("user_id"))
    course_name = doc.get("course_name") or _get_course_name(doc.get("course_id"))
    submitted = doc.get("submitted_at")
    return {
        "id": oid_str(doc["_id"]),
        "student_name": doc.get("guest_name") or (user.get("full_name") if user else "Khach"),
        "student_grade": doc.get("guest_grade") or (user.get("grade") if user else ""),
        "student_phone": doc.get("guest_phone") or (user.get("parent_phone") if user else ""),
        "course_name": course_name or "",
        "score": doc.get("score", 0),
        "recommendation": doc.get("recommendation", ""),
        "comment": doc.get("comment", ""),
        "duration_seconds": doc.get("duration_seconds", 0),
        "submitted_at": submitted,
    }


def build_test_details(questions, answers_map):
    details = []
    answers_map = _normalize_answers_map(answers_map)
    for q in questions:
        qid = str(q["id"])
        answer_id = answers_map.get(qid)
        selected = _find_answer(q, answer_id)
        correct = next((a for a in q["answers"] if a.get("is_correct")), None)
        details.append({
            "question_id": qid,
            "question_content": q.get("content"),
            "answer_id": str(answer_id) if answer_id else None,
            "answer_text": selected.get("answer_text") if selected else None,
            "is_correct": bool(selected and selected.get("is_correct")),
            "correct_answer": correct.get("answer_text") if correct else None,
            "category": q.get("category"),
            "level": q.get("level"),
        })
    return details


def _normalize_answers_map(answers_map):
    if not answers_map:
        return {}
    return {
        str(qid): str(aid)
        for qid, aid in answers_map.items()
        if aid is not None and aid != ""
    }


def _find_answer(question, answer_id):
    if not answer_id:
        return None
    target = str(answer_id)
    for answer in question.get("answers", []):
        aid = answer.get("id") or answer.get("_id")
        if aid is not None and str(aid) == target:
            return answer
    return None
