"""Quản lý lớp học, thành viên, điểm danh."""

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from database import col, oid_str, parse_oid

classrooms_bp = Blueprint("classrooms", __name__, url_prefix="/api/admin/classes")

ATTENDANCE_STATUSES = {"present", "absent", "late", "excused"}


def _admin_required():
    return get_jwt().get("role") == "admin"


def _dt(value):
    if isinstance(value, datetime):
        return value.isoformat() + "Z"
    return value


def class_to_dict(doc, member_count=None):
    if not doc:
        return None
    data = {
        "id": oid_str(doc["_id"]),
        "name": doc.get("name"),
        "year": int(doc.get("year") or 0),
        "schedule": doc.get("schedule") or "",
        "note": doc.get("note") or "",
        "created_at": _dt(doc.get("created_at")),
        "updated_at": _dt(doc.get("updated_at")),
    }
    if member_count is not None:
        data["member_count"] = member_count
    return data


def member_to_dict(doc):
    if not doc:
        return None
    return {
        "id": oid_str(doc["_id"]),
        "class_id": doc.get("class_id"),
        "name": doc.get("name"),
        "age": doc.get("age"),
        "phone": doc.get("phone") or "",
        "note": doc.get("note") or "",
        "created_at": _dt(doc.get("created_at")),
        "updated_at": _dt(doc.get("updated_at")),
    }


def attendance_to_dict(doc):
    if not doc:
        return None
    return {
        "id": oid_str(doc["_id"]),
        "class_id": doc.get("class_id"),
        "date": doc.get("date"),
        "note": doc.get("note") or "",
        "records": doc.get("records") or [],
        "created_at": _dt(doc.get("created_at")),
        "updated_at": _dt(doc.get("updated_at")),
    }


# ── Classes ─────────────────────────────────────────────

@classrooms_bp.route("", methods=["GET"])
@jwt_required()
def list_classes():
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403

    year = request.args.get("year")
    query = {}
    if year:
        try:
            query["year"] = int(year)
        except ValueError:
            return jsonify({"message": "Năm không hợp lệ"}), 400

    docs = list(col("classrooms").find(query).sort([("year", -1), ("name", 1)]))
    out = []
    for d in docs:
        count = col("class_members").count_documents({"class_id": oid_str(d["_id"])})
        out.append(class_to_dict(d, member_count=count))
    return jsonify(out)


@classrooms_bp.route("", methods=["POST"])
@jwt_required()
def create_class():
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    try:
        year = int(data.get("year"))
    except (TypeError, ValueError):
        return jsonify({"message": "Vui lòng nhập năm hợp lệ"}), 400

    if not name:
        return jsonify({"message": "Vui lòng nhập tên lớp"}), 400
    if year < 2000 or year > 2100:
        return jsonify({"message": "Năm phải trong khoảng 2000–2100"}), 400

    now = datetime.utcnow()
    doc = {
        "name": name,
        "year": year,
        "schedule": (data.get("schedule") or "").strip(),
        "note": (data.get("note") or "").strip(),
        "created_at": now,
        "updated_at": now,
    }
    result = col("classrooms").insert_one(doc)
    doc["_id"] = result.inserted_id
    return jsonify(class_to_dict(doc, member_count=0)), 201


@classrooms_bp.route("/<class_id>", methods=["GET"])
@jwt_required()
def get_class(class_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    doc = col("classrooms").find_one({"_id": parse_oid(class_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy lớp"}), 404
    count = col("class_members").count_documents({"class_id": str(doc["_id"])})
    return jsonify(class_to_dict(doc, member_count=count))


@classrooms_bp.route("/<class_id>", methods=["PUT"])
@jwt_required()
def update_class(class_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    doc = col("classrooms").find_one({"_id": parse_oid(class_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy lớp"}), 404

    data = request.get_json() or {}
    updates = {"updated_at": datetime.utcnow()}

    if "name" in data:
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"message": "Tên lớp không được trống"}), 400
        updates["name"] = name
    if "year" in data:
        try:
            year = int(data.get("year"))
        except (TypeError, ValueError):
            return jsonify({"message": "Năm không hợp lệ"}), 400
        if year < 2000 or year > 2100:
            return jsonify({"message": "Năm phải trong khoảng 2000–2100"}), 400
        updates["year"] = year
    if "schedule" in data:
        updates["schedule"] = (data.get("schedule") or "").strip()
    if "note" in data:
        updates["note"] = (data.get("note") or "").strip()

    col("classrooms").update_one({"_id": doc["_id"]}, {"$set": updates})
    doc = col("classrooms").find_one({"_id": doc["_id"]})
    count = col("class_members").count_documents({"class_id": str(doc["_id"])})
    return jsonify(class_to_dict(doc, member_count=count))


@classrooms_bp.route("/<class_id>", methods=["DELETE"])
@jwt_required()
def delete_class(class_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    oid = parse_oid(class_id)
    doc = col("classrooms").find_one({"_id": oid})
    if not doc:
        return jsonify({"message": "Không tìm thấy lớp"}), 404

    cid = str(oid)
    col("class_members").delete_many({"class_id": cid})
    col("attendance_sessions").delete_many({"class_id": cid})
    col("classrooms").delete_one({"_id": oid})
    return jsonify({"message": "Đã xóa lớp, thành viên và điểm danh liên quan"})


# ── Members ─────────────────────────────────────────────

@classrooms_bp.route("/<class_id>/members", methods=["GET"])
@jwt_required()
def list_members(class_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    if not col("classrooms").find_one({"_id": parse_oid(class_id)}):
        return jsonify({"message": "Không tìm thấy lớp"}), 404
    docs = col("class_members").find({"class_id": str(class_id)}).sort("name", 1)
    return jsonify([member_to_dict(d) for d in docs])


@classrooms_bp.route("/<class_id>/members", methods=["POST"])
@jwt_required()
def add_member(class_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    if not col("classrooms").find_one({"_id": parse_oid(class_id)}):
        return jsonify({"message": "Không tìm thấy lớp"}), 404

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"message": "Vui lòng nhập tên học sinh"}), 400

    age = data.get("age")
    if age is not None and age != "":
        try:
            age = int(age)
        except (TypeError, ValueError):
            return jsonify({"message": "Tuổi không hợp lệ"}), 400
        if age < 3 or age > 25:
            return jsonify({"message": "Tuổi nên trong khoảng 3–25"}), 400
    else:
        age = None

    phone = (data.get("phone") or "").strip().replace(" ", "")
    if phone and (not phone.isdigit() or not (9 <= len(phone) <= 11)):
        return jsonify({"message": "SĐT không hợp lệ (9–11 chữ số)"}), 400

    now = datetime.utcnow()
    doc = {
        "class_id": str(class_id),
        "name": name,
        "age": age,
        "phone": phone,
        "note": (data.get("note") or "").strip(),
        "created_at": now,
        "updated_at": now,
    }
    result = col("class_members").insert_one(doc)
    doc["_id"] = result.inserted_id
    return jsonify(member_to_dict(doc)), 201


@classrooms_bp.route("/<class_id>/members/<member_id>", methods=["PUT"])
@jwt_required()
def update_member(class_id, member_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    doc = col("class_members").find_one({
        "_id": parse_oid(member_id),
        "class_id": str(class_id),
    })
    if not doc:
        return jsonify({"message": "Không tìm thấy thành viên"}), 404

    data = request.get_json() or {}
    updates = {"updated_at": datetime.utcnow()}

    if "name" in data:
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"message": "Tên không được trống"}), 400
        updates["name"] = name
    if "age" in data:
        age = data.get("age")
        if age is None or age == "":
            updates["age"] = None
        else:
            try:
                age = int(age)
            except (TypeError, ValueError):
                return jsonify({"message": "Tuổi không hợp lệ"}), 400
            if age < 3 or age > 25:
                return jsonify({"message": "Tuổi nên trong khoảng 3–25"}), 400
            updates["age"] = age
    if "phone" in data:
        phone = (data.get("phone") or "").strip().replace(" ", "")
        if phone and (not phone.isdigit() or not (9 <= len(phone) <= 11)):
            return jsonify({"message": "SĐT không hợp lệ"}), 400
        updates["phone"] = phone
    if "note" in data:
        updates["note"] = (data.get("note") or "").strip()

    col("class_members").update_one({"_id": doc["_id"]}, {"$set": updates})
    doc = col("class_members").find_one({"_id": doc["_id"]})
    return jsonify(member_to_dict(doc))


@classrooms_bp.route("/<class_id>/members/<member_id>", methods=["DELETE"])
@jwt_required()
def delete_member(class_id, member_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    oid = parse_oid(member_id)
    doc = col("class_members").find_one({"_id": oid, "class_id": str(class_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy thành viên"}), 404

    # Xóa bản ghi điểm danh của thành viên này
    col("attendance_sessions").update_many(
        {"class_id": str(class_id)},
        {"$pull": {"records": {"member_id": str(oid)}}},
    )
    col("class_members").delete_one({"_id": oid})
    return jsonify({"message": "Đã xóa thành viên"})


# ── Attendance ──────────────────────────────────────────

@classrooms_bp.route("/<class_id>/attendance", methods=["GET"])
@jwt_required()
def list_attendance(class_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    if not col("classrooms").find_one({"_id": parse_oid(class_id)}):
        return jsonify({"message": "Không tìm thấy lớp"}), 404

    docs = col("attendance_sessions").find({"class_id": str(class_id)}).sort("date", -1)
    return jsonify([attendance_to_dict(d) for d in docs])


@classrooms_bp.route("/<class_id>/attendance/<date>", methods=["GET"])
@jwt_required()
def get_attendance(class_id, date):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    if not col("classrooms").find_one({"_id": parse_oid(class_id)}):
        return jsonify({"message": "Không tìm thấy lớp"}), 404

    doc = col("attendance_sessions").find_one({"class_id": str(class_id), "date": date})
    members = list(col("class_members").find({"class_id": str(class_id)}).sort("name", 1))
    member_list = [member_to_dict(m) for m in members]

    if not doc:
        # Trả về khung điểm danh trống
        return jsonify({
            "id": None,
            "class_id": str(class_id),
            "date": date,
            "note": "",
            "records": [
                {"member_id": m["id"], "status": "present", "note": ""}
                for m in member_list
            ],
            "members": member_list,
            "created_at": None,
            "updated_at": None,
        })

    data = attendance_to_dict(doc)
    data["members"] = member_list
    # Bổ sung thành viên mới chưa có trong records
    existing = {r.get("member_id") for r in data["records"]}
    for m in member_list:
        if m["id"] not in existing:
            data["records"].append({
                "member_id": m["id"],
                "status": "present",
                "note": "",
            })
    return jsonify(data)


@classrooms_bp.route("/<class_id>/attendance/<date>", methods=["PUT"])
@jwt_required()
def save_attendance(class_id, date):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    if not col("classrooms").find_one({"_id": parse_oid(class_id)}):
        return jsonify({"message": "Không tìm thấy lớp"}), 404

    # Validate date YYYY-MM-DD
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"message": "Ngày không hợp lệ (YYYY-MM-DD)"}), 400

    data = request.get_json() or {}
    raw_records = data.get("records") or []
    records = []
    for r in raw_records:
        mid = str(r.get("member_id") or "")
        status = (r.get("status") or "present").lower()
        if status not in ATTENDANCE_STATUSES:
            status = "present"
        if not mid:
            continue
        records.append({
            "member_id": mid,
            "status": status,
            "note": (r.get("note") or "").strip(),
        })

    now = datetime.utcnow()
    existing = col("attendance_sessions").find_one({"class_id": str(class_id), "date": date})
    payload = {
        "class_id": str(class_id),
        "date": date,
        "note": (data.get("note") or "").strip(),
        "records": records,
        "updated_at": now,
    }

    if existing:
        col("attendance_sessions").update_one({"_id": existing["_id"]}, {"$set": payload})
        doc = col("attendance_sessions").find_one({"_id": existing["_id"]})
    else:
        payload["created_at"] = now
        result = col("attendance_sessions").insert_one(payload)
        doc = col("attendance_sessions").find_one({"_id": result.inserted_id})

    return jsonify(attendance_to_dict(doc))


@classrooms_bp.route("/<class_id>/attendance/<date>", methods=["DELETE"])
@jwt_required()
def delete_attendance(class_id, date):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    result = col("attendance_sessions").delete_one({"class_id": str(class_id), "date": date})
    if result.deleted_count == 0:
        return jsonify({"message": "Không tìm thấy buổi điểm danh"}), 404
    return jsonify({"message": "Đã xóa buổi điểm danh"})
