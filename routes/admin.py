from flask import Blueprint, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt
from database import col, parse_oid, oid_str
from models import user_to_dict, test_to_dict, test_for_export
from services.export import export_tests_excel, export_tests_pdf, _public_detail_url

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def admin_required():
    claims = get_jwt()
    return claims.get("role") == "admin"


@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    if not admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403

    total_students = col("users").count_documents({"role": "student"})
    total_tests = col("tests").count_documents({})

    pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$score"}}}]
    avg_result = list(col("tests").aggregate(pipeline))
    avg_score = avg_result[0]["avg"] if avg_result else 0

    scratch = col("courses").find_one({"slug": "scratch"})
    python = col("courses").find_one({"slug": "python"})

    scratch_id = oid_str(scratch["_id"]) if scratch else None
    python_id = oid_str(python["_id"]) if python else None

    scratch_count = col("tests").count_documents({"course_id": scratch_id}) if scratch_id else 0
    python_count = col("tests").count_documents({"course_id": python_id}) if python_id else 0

    total_course_tests = scratch_count + python_count
    scratch_pct = round((scratch_count / total_course_tests) * 100, 1) if total_course_tests else 0
    python_pct = round((python_count / total_course_tests) * 100, 1) if total_course_tests else 0

    score_ranges = {"0-40": 0, "41-70": 0, "71-100": 0}
    for test in col("tests").find({}, {"score": 1}):
        s = test.get("score", 0)
        if s <= 40:
            score_ranges["0-40"] += 1
        elif s <= 70:
            score_ranges["41-70"] += 1
        else:
            score_ranges["71-100"] += 1

    recent = col("tests").find().sort("submitted_at", -1).limit(10)

    return jsonify({
        "total_students": total_students,
        "total_tests": total_tests,
        "avg_score": round(float(avg_score), 1),
        "scratch_count": scratch_count,
        "python_count": python_count,
        "scratch_percentage": scratch_pct,
        "python_percentage": python_pct,
        "score_ranges": score_ranges,
        "recent_tests": [test_to_dict(t) for t in recent],
    })


@admin_bp.route("/students", methods=["GET"])
@jwt_required()
def get_students():
    if not admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403

    students = col("users").find({"role": "student"}).sort("created_at", -1)
    result = []
    for s in students:
        data = user_to_dict(s)
        data["test_count"] = col("tests").count_documents({"user_id": data["id"]})
        result.append(data)
    return jsonify(result)


@admin_bp.route("/tests", methods=["GET"])
@jwt_required()
def get_all_tests():
    if not admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    tests = col("tests").find().sort("submitted_at", -1)
    return jsonify([test_to_dict(t) for t in tests])


@admin_bp.route("/tests/<test_id>", methods=["GET"])
@jwt_required()
def get_test_detail(test_id):
    if not admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    doc = col("tests").find_one({"_id": parse_oid(test_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy bài test"}), 404
    return jsonify(test_to_dict(doc, include_details=True))


@admin_bp.route("/tests/<test_id>", methods=["DELETE"])
@jwt_required()
def delete_test(test_id):
    if not admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    result = col("tests").delete_one({"_id": parse_oid(test_id)})
    if result.deleted_count == 0:
        return jsonify({"message": "Không tìm thấy bài test"}), 404
    return jsonify({"message": "Đã xóa bài làm"})


@admin_bp.route("/export/excel", methods=["GET"])
@jwt_required()
def export_excel():
    if not admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    tests = []
    frontend_url = current_app.config.get("FRONTEND_URL")
    for t in col("tests").find().sort("submitted_at", -1):
        row = test_for_export(t)
        row["detail_url"] = _public_detail_url(row["id"], frontend_url)
        tests.append(row)
    output = export_tests_excel(tests, frontend_url)
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="ket_qua_kiem_tra.xlsx",
    )


@admin_bp.route("/export/pdf", methods=["GET"])
@jwt_required()
def export_pdf():
    if not admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    tests = [test_for_export(t) for t in col("tests").find().sort("submitted_at", -1)]
    output = export_tests_pdf(tests)
    return send_file(
        output,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="ket_qua_kiem_tra.pdf",
    )
