from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from database import col, parse_oid, oid_str
from models import question_to_dict, test_to_dict, build_test_details
from services.scoring import calculate_scores, get_comment, get_recommendation

tests_bp = Blueprint("tests", __name__, url_prefix="/api/tests")


def _get_questions_for_course(course_id, include_correct=False):
    docs = col("questions").find({"course_id": str(course_id)}).sort("order_num", 1)
    return [question_to_dict(q, include_correct=include_correct) for q in docs]


@tests_bp.route("/start", methods=["POST"])
def start_test():
    data = request.get_json()
    course_id = data.get("course_id")
    course_slug = data.get("course_slug")

    course = None
    if course_slug and not course_id:
        course = col("courses").find_one({"slug": course_slug})
        course_id = oid_str(course["_id"]) if course else None
    elif course_id:
        course = col("courses").find_one({"_id": parse_oid(course_id)})

    if not course_id or not course:
        return jsonify({"message": "Không tìm thấy khóa học"}), 404

    questions = _get_questions_for_course(course_id)
    return jsonify({
        "course_id": course_id,
        "total_questions": len(questions),
        "questions": questions,
    })


@tests_bp.route("/submit", methods=["POST"])
def submit_test():
    data = request.get_json()
    course_id = str(data.get("course_id"))
    answers = data.get("answers", {})
    duration = data.get("duration_seconds", 0)
    guest_name = (data.get("guest_name") or "").strip()
    guest_grade = (data.get("guest_grade") or "").strip()
    guest_phone = (data.get("guest_phone") or "").strip()

    if not guest_name or not guest_grade or not guest_phone:
        return jsonify({"message": "Vui lòng nhập đầy đủ họ tên, lớp và số điện thoại"}), 400

    course = col("courses").find_one({"_id": parse_oid(course_id)})
    if not course:
        return jsonify({"message": "Không tìm thấy khóa học"}), 404

    questions = _get_questions_for_course(course_id, include_correct=True)
    score, radar_scores = calculate_scores(questions, answers)
    comment = get_comment(score)
    recommendation = get_recommendation(course.get("slug"), score)

    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            user_id = identity
    except Exception:
        pass

    test_doc = {
        "user_id": user_id,
        "course_id": course_id,
        "course_name": course.get("name"),
        "score": score,
        "radar_scores": radar_scores,
        "recommendation": recommendation,
        "comment": comment,
        "duration_seconds": duration,
        "guest_name": guest_name,
        "guest_grade": guest_grade,
        "guest_phone": guest_phone,
        "details": build_test_details(questions, answers),
        "submitted_at": datetime.utcnow(),
    }
    result = col("tests").insert_one(test_doc)
    test_doc["_id"] = result.inserted_id
    return jsonify(test_to_dict(test_doc)), 201


@tests_bp.route("/result/<test_id>", methods=["GET"])
def get_result(test_id):
    doc = col("tests").find_one({"_id": parse_oid(test_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy kết quả"}), 404
    return jsonify(test_to_dict(doc))


@tests_bp.route("/result/<test_id>/public", methods=["GET"])
def get_result_public(test_id):
    """Chi tiết bài làm công khai — phụ huynh xem qua link (không cần đăng nhập)."""
    doc = col("tests").find_one({"_id": parse_oid(test_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy bài làm"}), 404
    return jsonify(test_to_dict(doc, include_details=True))


@tests_bp.route("/achievements", methods=["GET"])
def get_achievements():
    tests = (
        col("tests")
        .find({"score": {"$gt": 0}})
        .sort([("score", -1), ("submitted_at", -1)])
        .limit(4)
    )
    result = []
    for t in tests:
        result.append({
            "name": t.get("guest_name") or "Học sinh",
            "score": t.get("score", 0),
            "course": t.get("course_name") or "",
        })
    return jsonify(result)


@tests_bp.route("/my-results", methods=["GET"])
@jwt_required()
def my_results():
    user_id = get_jwt_identity()
    tests = col("tests").find({"user_id": user_id}).sort("submitted_at", -1)
    return jsonify([test_to_dict(t) for t in tests])


@tests_bp.route("/result/<test_id>/details", methods=["GET"])
@jwt_required()
def get_result_details(test_id):
    doc = col("tests").find_one({"_id": parse_oid(test_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy kết quả"}), 404
    return jsonify(test_to_dict(doc, include_details=True))
