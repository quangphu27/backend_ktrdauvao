"""Kiểm tra toàn bộ câu hỏi: đáp án không trùng, có đúng 1 đáp án đúng, chấm điểm đúng."""
import random
from bson import ObjectId

from database import col, oid_str
from models import question_to_dict
from routes.tests import _get_questions_for_course
from services.scoring import calculate_scores
from seed import SCRATCH_QUESTIONS, PYTHON_QUESTIONS, _build_answers, _validate_answers


def _check_seed_question(course_name, index, q):
    errors = []
    content = q.get("content", "")
    answers = q.get("answers", [])
    correct_idx = q.get("correct", 0)

    if len(answers) != 4:
        errors.append(f"{course_name} #{index}: cần 4 đáp án, có {len(answers)}")
    if correct_idx < 0 or correct_idx >= len(answers):
        errors.append(f"{course_name} #{index}: chỉ số đáp án đúng không hợp lệ ({correct_idx})")
    try:
        _validate_answers(answers, content)
    except ValueError as e:
        errors.append(f"{course_name} #{index}: {e}")

    # Kiểm tra sau khi xáo trộn vẫn có đúng 1 đáp án đúng
    for trial in range(5):
        random.seed(trial)
        built = _build_answers(list(answers), correct_idx, content)
        correct_answers = [a for a in built if a.get("is_correct") is True]
        if len(correct_answers) != 1:
            errors.append(
                f"{course_name} #{index}: sau xáo trộn có {len(correct_answers)} đáp án đúng (cần 1)"
            )
            break
        expected_text = answers[correct_idx]
        if correct_answers[0]["answer_text"] != expected_text:
            errors.append(
                f"{course_name} #{index}: nội dung đáp án đúng không khớp seed"
            )
            break

    return errors


def _check_db_question(doc):
    errors = []
    qid = oid_str(doc["_id"])
    content = doc.get("content", "")[:50]
    answers = doc.get("answers", [])
    texts = [a.get("answer_text", "").strip().lower() for a in answers]

    if len(texts) != len(set(texts)):
        errors.append(f"DB {qid}: đáp án trùng nhau — {content}")
    correct = [a for a in answers if a.get("is_correct") is True]
    if len(correct) != 1:
        errors.append(f"DB {qid}: có {len(correct)} đáp án đúng (cần 1) — {content}")
    for a in answers:
        if not a.get("id"):
            errors.append(f"DB {qid}: thiếu id đáp án — {content}")
            break

    return errors


def _test_scoring(course_slug):
    errors = []
    course = col("courses").find_one({"slug": course_slug})
    if not course:
        return [f"Không tìm thấy khóa {course_slug}"]

    cid = oid_str(course["_id"])
    questions = _get_questions_for_course(cid, include_correct=True)

    if len(questions) != 30:
        errors.append(f"{course_slug}: có {len(questions)} câu (cần 30)")

    all_correct = {}
    for q in questions:
        correct = next((a for a in q["answers"] if a.get("is_correct")), None)
        if not correct:
            errors.append(f"{course_slug} q={q['id']}: không có đáp án đúng")
            continue
        all_correct[str(q["id"])] = str(correct["id"])

    score, _ = calculate_scores(questions, all_correct)
    if score != 100.0:
        errors.append(f"{course_slug}: chọn đúng hết nhưng điểm = {score} (cần 100)")

    # Chọn sai hết → 0 điểm
    all_wrong = {}
    for q in questions:
        wrong = next((a for a in q["answers"] if not a.get("is_correct")), None)
        if wrong:
            all_wrong[str(q["id"])] = str(wrong["id"])
    score_wrong, _ = calculate_scores(questions, all_wrong)
    if score_wrong != 0.0:
        errors.append(f"{course_slug}: chọn sai hết nhưng điểm = {score_wrong} (cần 0)")

    return errors


def validate_all():
    all_errors = []

    for name, qs in [("Scratch", SCRATCH_QUESTIONS), ("Python", PYTHON_QUESTIONS)]:
        for i, q in enumerate(qs, 1):
            all_errors.extend(_check_seed_question(name, i, q))

    for doc in col("questions").find():
        all_errors.extend(_check_db_question(doc))

    for slug in ("scratch", "python"):
        all_errors.extend(_test_scoring(slug))

    return all_errors


if __name__ == "__main__":
    from app import create_app

    app = create_app()
    with app.app_context():
        errors = validate_all()
        if errors:
            print(f"LOI ({len(errors)}):")
            for e in errors:
                print(f"  - {e}")
            raise SystemExit(1)
        print("OK: 60 cau seed + DB + cham diem deu hop le.")
