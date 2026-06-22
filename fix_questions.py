import random
from bson import ObjectId

from database import col


def _normalize_answer_id(answer):
    return str(answer.get("id") or answer.get("_id") or "")


import random
from bson import ObjectId

from database import col
from seed import _validate_answers, _validate_correct_index


def _build_shuffled_answers(answer_texts, correct_index, content=""):
    _validate_answers(answer_texts, content)
    _validate_correct_index(answer_texts, correct_index, content)
    items = [
        {"answer_text": text, "is_correct": i == correct_index}
        for i, text in enumerate(answer_texts)
    ]
    random.shuffle(items)
    for item in items:
        item["id"] = str(ObjectId())
    return items


def _extract_answer_texts_and_correct(answers):
    texts = [a.get("answer_text", "") for a in answers]
    correct_indices = [i for i, a in enumerate(answers) if a.get("is_correct")]
    if len(correct_indices) == 1:
        return texts, correct_indices[0]
    if len(correct_indices) == 0:
        return texts, 0
    return texts, correct_indices[0]


def fix_all_questions():
    """Xáo trộn đáp án và đảm bảo mỗi câu có đúng 1 đáp án đúng + id."""
    updated = 0
    for doc in col("questions").find():
        answers = doc.get("answers", [])
        if not answers:
            continue

        texts, correct_idx = _extract_answer_texts_and_correct(answers)
        if len(texts) < 2:
            continue

        content = doc.get("content", "")
        new_answers = _build_shuffled_answers(texts, correct_idx, content)
        col("questions").update_one(
            {"_id": doc["_id"]},
            {"$set": {"answers": new_answers}},
        )
        updated += 1

    print(f"Da cap nhat {updated} cau hoi.")
    return updated


if __name__ == "__main__":
    from app import create_app

    app = create_app()
    with app.app_context():
        fix_all_questions()
