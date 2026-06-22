import os
import random
import uuid
from bson import ObjectId
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request
from database import col, parse_oid, oid_str
from models import question_to_dict

questions_bp = Blueprint("questions", __name__, url_prefix="/api/questions")


def _validate_unique_answers(answer_list):
    texts = [a.get("answer_text", "").strip().lower() for a in answer_list]
    if len(texts) != len(set(texts)):
        return "Các đáp án không được trùng nhau"
    if len(texts) < 2:
        return "Cần ít nhất 2 đáp án"
    return None


def admin_required():
    claims = get_jwt()
    return claims.get("role") == "admin"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


def _build_answers(answer_list):
    items = [
        {"answer_text": ans["answer_text"], "is_correct": ans.get("is_correct", False)}
        for ans in answer_list
    ]
    random.shuffle(items)
    answers = []
    for item in items:
        answers.append({
            "id": str(ObjectId()),
            "answer_text": item["answer_text"],
            "is_correct": item["is_correct"],
        })
    return answers


@questions_bp.route("", methods=["GET"])
def get_questions():
    course_id = request.args.get("course_id")
    course_slug = request.args.get("course_slug")
    include_correct = request.args.get("include_correct", "false").lower() == "true"

    query = {}
    if course_id:
        query["course_id"] = str(course_id)
    elif course_slug:
        course = col("courses").find_one({"slug": course_slug})
        if course:
            query["course_id"] = oid_str(course["_id"])

    is_admin = False
    try:
        verify_jwt_in_request(optional=True)
        claims = get_jwt()
        if claims:
            is_admin = claims.get("role") == "admin"
    except Exception:
        pass

    questions = col("questions").find(query).sort("order_num", 1)
    return jsonify([
        question_to_dict(q, include_correct=include_correct and is_admin)
        for q in questions
    ])


@questions_bp.route("/<question_id>", methods=["GET"])
def get_question(question_id):
    doc = col("questions").find_one({"_id": parse_oid(question_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy câu hỏi"}), 404
    return jsonify(question_to_dict(doc, include_correct=False))


@questions_bp.route("", methods=["POST"])
@jwt_required()
def create_question():
    if not admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403

    data = request.get_json()
    err = _validate_unique_answers(data.get("answers", []))
    if err:
        return jsonify({"message": err}), 400
    doc = {
        "course_id": str(data["course_id"]),
        "content": data["content"],
        "image_url": data.get("image_url"),
        "level": data.get("level", "easy"),
        "category": data.get("category", "logic"),
        "order_num": data.get("order_num", 0),
        "answers": _build_answers(data.get("answers", [])),
    }
    result = col("questions").insert_one(doc)
    doc["_id"] = result.inserted_id
    return jsonify(question_to_dict(doc, include_correct=True)), 201


@questions_bp.route("/<question_id>", methods=["PUT"])
@jwt_required()
def update_question(question_id):
    if not admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403

    doc = col("questions").find_one({"_id": parse_oid(question_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy câu hỏi"}), 404

    data = request.get_json()
    update = {
        "content": data.get("content", doc.get("content")),
        "image_url": data.get("image_url", doc.get("image_url")),
        "level": data.get("level", doc.get("level")),
        "category": data.get("category", doc.get("category")),
        "order_num": data.get("order_num", doc.get("order_num")),
        "course_id": str(data.get("course_id", doc.get("course_id"))),
    }
    if "answers" in data:
        err = _validate_unique_answers(data["answers"])
        if err:
            return jsonify({"message": err}), 400
        update["answers"] = _build_answers(data["answers"])

    col("questions").update_one({"_id": doc["_id"]}, {"$set": update})
    updated = col("questions").find_one({"_id": doc["_id"]})
    return jsonify(question_to_dict(updated, include_correct=True))


@questions_bp.route("/<question_id>", methods=["DELETE"])
@jwt_required()
def delete_question(question_id):
    if not admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403

    result = col("questions").delete_one({"_id": parse_oid(question_id)})
    if result.deleted_count == 0:
        return jsonify({"message": "Không tìm thấy câu hỏi"}), 404
    return jsonify({"message": "Đã xóa câu hỏi"})


@questions_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_image():
    if not admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403

    if "file" not in request.files:
        return jsonify({"message": "Không có file"}), 400

    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"message": "File không hợp lệ"}), 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    return jsonify({"image_url": f"/uploads/{filename}"})
