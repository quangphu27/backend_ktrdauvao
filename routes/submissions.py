"""Nộp bài Scratch 3 — học sinh upload, admin xem."""

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from werkzeug.utils import secure_filename

from database import col, oid_str, parse_oid
from services.cloudinary_service import destroy_file, upload_submission_file

submissions_bp = Blueprint("submissions", __name__, url_prefix="/api/submissions")


def _admin_required():
    claims = get_jwt()
    return claims.get("role") == "admin"


def _allowed_file(filename, allowed):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def _submission_to_dict(doc):
    return {
        "id": oid_str(doc.get("_id")),
        "student_name": doc.get("student_name"),
        "grade": doc.get("grade"),
        "phone": doc.get("phone"),
        "note": doc.get("note") or "",
        "files": doc.get("files") or [],
        "submitted_at": (
            doc["submitted_at"].isoformat() + "Z"
            if isinstance(doc.get("submitted_at"), datetime)
            else doc.get("submitted_at")
        ),
    }


@submissions_bp.route("/scratch3", methods=["POST"])
def submit_scratch3():
    """Học sinh nộp bài Scratch 3 (multipart)."""
    name = (request.form.get("student_name") or "").strip()
    grade = (request.form.get("grade") or "").strip()
    phone = (request.form.get("phone") or "").strip().replace(" ", "")
    note = (request.form.get("note") or "").strip()

    if not name or not grade or not phone:
        return jsonify({"message": "Vui lòng nhập đầy đủ họ tên, lớp và số điện thoại"}), 400
    if not phone.isdigit() or not (9 <= len(phone) <= 11):
        return jsonify({"message": "Số điện thoại không hợp lệ (9–11 chữ số)"}), 400

    files = request.files.getlist("files") or []
    if not files and request.files.get("file"):
        files = [request.files.get("file")]
    files = [f for f in files if f and f.filename]
    if not files:
        return jsonify({"message": "Vui lòng chọn ít nhất 1 file để nộp"}), 400
    if len(files) > 10:
        return jsonify({"message": "Tối đa 10 file mỗi lần nộp"}), 400

    from flask import current_app

    allowed = current_app.config.get("ALLOWED_SUBMISSION_EXTENSIONS") or set()
    uploaded = []
    try:
        for f in files:
            filename = secure_filename(f.filename) or f.filename
            if not _allowed_file(filename, allowed):
                return jsonify({
                    "message": (
                        f"File «{f.filename}» không được hỗ trợ. "
                        f"Cho phép: {', '.join(sorted(allowed))}"
                    ),
                }), 400
            uploaded.append(upload_submission_file(f, name, phone))
    except Exception as exc:
        for item in uploaded:
            try:
                destroy_file(item.get("public_id"), item.get("resource_type") or "raw")
            except Exception:
                pass
        return jsonify({"message": f"Upload Cloudinary thất bại: {exc}"}), 500

    doc = {
        "student_name": name,
        "grade": grade,
        "phone": phone,
        "note": note,
        "files": uploaded,
        "submitted_at": datetime.utcnow(),
        "type": "scratch3",
    }
    result = col("scratch_submissions").insert_one(doc)
    doc["_id"] = result.inserted_id
    return jsonify({
        "message": "Nộp bài thành công!",
        "submission": _submission_to_dict(doc),
    }), 201


@submissions_bp.route("/scratch3", methods=["GET"])
@jwt_required()
def list_scratch3():
    """Admin: danh sách bài nộp Scratch 3."""
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403

    q = (request.args.get("q") or "").strip()
    query = {"type": "scratch3"}
    if q:
        query["$or"] = [
            {"student_name": {"$regex": q, "$options": "i"}},
            {"phone": {"$regex": q, "$options": "i"}},
            {"grade": {"$regex": q, "$options": "i"}},
        ]

    docs = col("scratch_submissions").find(query).sort("submitted_at", -1)
    return jsonify([_submission_to_dict(d) for d in docs])


@submissions_bp.route("/scratch3/<submission_id>", methods=["GET"])
@jwt_required()
def get_scratch3(submission_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    doc = col("scratch_submissions").find_one({"_id": parse_oid(submission_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy bài nộp"}), 404
    return jsonify(_submission_to_dict(doc))


@submissions_bp.route("/scratch3/<submission_id>", methods=["DELETE"])
@jwt_required()
def delete_scratch3(submission_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    doc = col("scratch_submissions").find_one({"_id": parse_oid(submission_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy bài nộp"}), 404

    for item in doc.get("files") or []:
        try:
            destroy_file(item.get("public_id"), item.get("resource_type") or "raw")
        except Exception:
            pass

    col("scratch_submissions").delete_one({"_id": doc["_id"]})
    return jsonify({"message": "Đã xóa bài nộp"})
