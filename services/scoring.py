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


def get_recommendation(course_slug, score):
    if course_slug == "scratch":
        if score <= 40:
            return "Scratch Junior"
        if score <= 70:
            return "Scratch cơ bản"
        return "Scratch nâng cao"
    if score <= 40:
        return "Tin học cơ bản"
    if score <= 70:
        return "Python Kids Beginner"
    return "Python Kids Intermediate"


def calculate_scores(questions, answers_map):
    total = len(questions)
    correct_count = 0
    category_stats = {}

    for q in questions:
        radar_cat = CATEGORY_MAP.get(q.get("category"), "Logic")
        if radar_cat not in category_stats:
            category_stats[radar_cat] = {"correct": 0, "total": 0}
        category_stats[radar_cat]["total"] += 1

        qid = q["id"]
        selected_id = answers_map.get(str(qid)) or answers_map.get(qid)
        if selected_id:
            correct_answer = next((a for a in q.get("answers", []) if a.get("is_correct")), None)
            if correct_answer and str(selected_id) == str(correct_answer["id"]):
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
