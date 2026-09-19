from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from pymongo.errors import PyMongoError
from database import col, parse_oid
from models import user_to_dict, is_user_approved, hash_password, verify_password

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    required = ["full_name", "email", "password"]
    for field in required:
        if not data.get(field):
            return jsonify({"message": f"Thiếu trường {field}"}), 400

    if col("users").find_one({"email": data["email"]}):
        return jsonify({"message": "Email đã được sử dụng"}), 400

    user_doc = {
        "full_name": data["full_name"],
        "email": data["email"],
        "password_hash": hash_password(data["password"]),
        "role": "student",
        "approval_status": "pending",
        "grade": data.get("grade"),
        "school": data.get("school"),
        "parent_email": data.get("parent_email"),
        "parent_phone": data.get("parent_phone"),
        "created_at": datetime.utcnow(),
    }
    if data.get("date_of_birth"):
        user_doc["date_of_birth"] = datetime.strptime(data["date_of_birth"], "%Y-%m-%d").date()

    result = col("users").insert_one(user_doc)
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
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"message": "Vui lòng nhập email và mật khẩu"}), 400

    try:
        doc = col("users").find_one({"email": email})
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
    token = create_access_token(identity=user["id"], additional_claims={"role": user["role"]})
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
