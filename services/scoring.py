CATEGORY_MAP = {
    "logic": "Logic",
    "observation": "Creative",
    "problem_solving": "Logic",
    "sequencing": "Algorithm",
    "memory": "Memory",
    "math": "Math",
    "algorithm": "Algorithm",
}

RADAR_CATEGORIES = ["Logic", "Creative", "Math", "Algorithm", "Memory"]


def get_comment(score):
    if score <= 40:
        return "Cần thêm thời gian làm quen với máy tính."
    if score <= 70:
        return "Con đã có nền tảng khá tốt."
    return "Con có tố chất học lập trình rất tốt."


def get_recommendation(course_slug, score, phone=None, student_name=None):
    from services.class_assignment import get_recommendation as _class_rec
    return _class_rec(course_slug, score, phone, student_name)


def _normalize_answers_map(answers_map):
    """Chuẩn hóa map câu trả lời: key/value đều là string."""
    if not answers_map:
        return {}
    normalized = {}
    for qid, aid in answers_map.items():
        if aid is not None and aid != "":
            normalized[str(qid)] = str(aid)
    return normalized


def _find_answer(question, answer_id):
    if not answer_id:
        return None
    target = str(answer_id)
    for answer in question.get("answers", []):
        aid = answer.get("id") or answer.get("_id")
        if aid is not None and str(aid) == target:
            return answer
    return None


def calculate_scores(questions, answers_map):
    total = len(questions)
    correct_count = 0
    category_stats = {}
    answers_map = _normalize_answers_map(answers_map)

    for q in questions:
        radar_cat = CATEGORY_MAP.get(q.get("category"), "Logic")
        if radar_cat not in category_stats:
            category_stats[radar_cat] = {"correct": 0, "total": 0}
        category_stats[radar_cat]["total"] += 1

        qid = str(q["id"])
        selected_id = answers_map.get(qid)
        selected = _find_answer(q, selected_id)

        if selected and selected.get("is_correct") is True:
            correct_count += 1
            category_stats[radar_cat]["correct"] += 1

    score = round((correct_count / total) * 100, 1) if total > 0 else 0

    radar_scores = {}
    for cat in RADAR_CATEGORIES:
        stats = category_stats.get(cat, {"correct": 0, "total": 0})
        if stats["total"] > 0:
            radar_scores[cat] = round((stats["correct"] / stats["total"]) * 100, 1)
        else:
            radar_scores[cat] = 0

    return score, radar_scores
