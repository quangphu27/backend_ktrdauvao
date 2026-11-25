import re
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from pymongo.errors import PyMongoError
from database import col, parse_oid
from models import user_to_dict, is_user_approved, hash_password, verify_password

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    required = ["full_name", "email", "password"]
    for field in required:
        if not str(data.get(field) or "").strip():
            return jsonify({"message": f"Thiếu trường {field}"}), 400

    email = str(data["email"]).strip().lower()
    full_name = str(data["full_name"]).strip()
    password = str(data["password"])
    if len(password) < 6:
        return jsonify({"message": "Mật khẩu phải có ít nhất 6 ký tự"}), 400

    if col("users").find_one({"email": email}) or col("users").find_one(
        {"email": {"$regex": f"^{re.escape(email)}$", "$options": "i"}}
    ):
        return jsonify({"message": "Email đã được sử dụng"}), 400

    user_doc = {
        "full_name": full_name,
        "email": email,
        # Index unique username_1 (không sparse) → phải có giá trị unique, dùng email
        "username": email,
        "password_hash": hash_password(password),
        "role": "student",
        "approval_status": "pending",
        "grade": (str(data.get("grade") or "").strip() or None),
        "school": (str(data.get("school") or "").strip() or None),
        "parent_email": (str(data.get("parent_email") or "").strip().lower() or None),
        "parent_phone": (str(data.get("parent_phone") or "").strip() or None),
        "created_at": datetime.utcnow(),
    }
    dob_raw = str(data.get("date_of_birth") or "").strip()
    if dob_raw:
        try:
            # BSON không encode datetime.date → phải dùng datetime
            user_doc["date_of_birth"] = datetime.strptime(dob_raw, "%Y-%m-%d")
        except ValueError:
            return jsonify({"message": "Ngày sinh không hợp lệ (YYYY-MM-DD)"}), 400

    try:
        result = col("users").insert_one(user_doc)
    except PyMongoError as e:
        return jsonify({"message": f"Không lưu được tài khoản: {e}"}), 503

    user_doc["_id"] = result.inserted_id
    user = user_to_dict(user_doc)

    # Không cấp token — phải chờ admin duyệt mới đăng nhập được
    return jsonify({
        "message": (
            "Đăng ký thành công! Tài khoản đang chờ admin duyệt. "
            "Bạn sẽ đăng nhập được sau khi được phê duyệt."
        ),
        "user": user,
        "pending_approval": True,
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = str(data.get("email") or "").strip().lower()
    password = data.get("password")
    if not email or not password:
        return jsonify({"message": "Vui lòng nhập email và mật khẩu"}), 400

    try:
        doc = col("users").find_one({"email": email})
        if not doc:
            doc = col("users").find_one(
                {"email": {"$regex": f"^{re.escape(email)}$", "$options": "i"}}
            )
    except PyMongoError as e:
        return jsonify({"message": f"Không kết nối được database: {e}"}), 503
    if not doc or not verify_password(doc.get("password_hash", ""), password):
        return jsonify({"message": "Email hoặc mật khẩu không đúng"}), 401

    status = doc.get("approval_status")
    if not is_user_approved(doc):
        if status == "rejected":
            return jsonify({
                "message": "Tài khoản đã bị từ chối. Vui lòng liên hệ admin.",
            }), 403
        return jsonify({
            "message": "Tài khoản đang chờ admin duyệt. Vui lòng thử lại sau.",
        }), 403

    user = user_to_dict(doc)
    # flask-jwt-extended 4.x: identity phải là string
    token = create_access_token(
        identity=str(user["id"]),
        additional_claims={"role": user.get("role") or "student"},
    )
    return jsonify({"token": token, "user": user})


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    doc = col("users").find_one({"_id": parse_oid(user_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy người dùng"}), 404
    if not is_user_approved(doc):
        return jsonify({"message": "Tài khoản chưa được duyệt"}), 403
    return jsonify(user_to_dict(doc))
