"""API bài kiểm tra tự tạo — admin CRUD + học sinh làm bài."""

from datetime import datetime
from io import BytesIO

from flask import Blueprint, current_app, jsonify, request, send_file
from flask_jwt_extended import get_jwt, jwt_required, verify_jwt_in_request
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from werkzeug.utils import secure_filename

from database import col, parse_oid, oid_str
from services.cloudinary_service import upload_image_file, upload_submission_file
from services.quiz_service import (
    attempt_to_dict,
    generate_quiz_slug,
    grade_attempt,
    quiz_to_dict,
    recompute_attempt_score,
    sanitize_questions,
)

quizzes_bp = Blueprint("quizzes", __name__, url_prefix="/api/quizzes")


def _admin_required():
    return get_jwt().get("role") == "admin"


def _unique_slug():
    for _ in range(20):
        slug = generate_quiz_slug()
        if not col("quizzes").find_one({"slug": slug}):
            return slug
    return generate_quiz_slug(12)


# ── Public ──────────────────────────────────────────────

@quizzes_bp.route("/by-slug/<slug>", methods=["GET"])
def get_quiz_public(slug):
    doc = col("quizzes").find_one({"slug": slug, "is_active": True})
    if not doc:
        return jsonify({"message": "Không tìm thấy bài kiểm tra hoặc đã tắt"}), 404
    data = quiz_to_dict(doc, include_answers=False)
    # Không trả danh sách câu hỏi đầy đủ ở bước info — chỉ meta
    data["questions"] = []
    return jsonify(data)


def _is_admin_request():
    try:
        verify_jwt_in_request(optional=True)
        return get_jwt().get("role") == "admin"
    except Exception:
        return False


@quizzes_bp.route("/by-slug/<slug>/start", methods=["POST"])
def start_quiz(slug):
    doc = col("quizzes").find_one({"slug": slug, "is_active": True})
    if not doc:
        return jsonify({"message": "Không tìm thấy bài kiểm tra hoặc đã tắt"}), 404
    include_explanations = _is_admin_request()
    return jsonify(quiz_to_dict(doc, include_answers=False, include_explanations=include_explanations))


@quizzes_bp.route("/by-slug/<slug>/submit", methods=["POST"])
def submit_quiz(slug):
    doc = col("quizzes").find_one({"slug": slug, "is_active": True})
    if not doc:
        return jsonify({"message": "Không tìm thấy bài kiểm tra hoặc đã tắt"}), 404

    data = request.get_json() or {}
    name = (data.get("student_name") or "").strip()
    grade = (data.get("student_grade") or data.get("grade") or "").strip()
    phone = (data.get("student_phone") or data.get("phone") or "").strip().replace(" ", "")
    answers = data.get("answers") or {}
    code_grades = data.get("code_grades") or {}
    duration = int(data.get("duration_seconds") or 0)

    if not name or not grade:
        return jsonify({"message": "Vui lòng nhập họ tên và lớp"}), 400

    graded = grade_attempt(doc, answers, code_grades=code_grades)
    attempt = {
        "quiz_id": str(doc["_id"]),
        "quiz_title": doc.get("title"),
        "quiz_slug": doc.get("slug"),
        "student_name": name,
        "student_grade": grade,
        "student_phone": phone,
        "answers": {str(k): v for k, v in answers.items()},
        "details": graded["details"],
        "earned": graded["earned"],
        "max_score": graded["max_score"],
        "score": graded["score"],
        "pending_manual": graded.get("pending_manual") or 0,
        "duration_seconds": duration,
        "submitted_at": datetime.utcnow(),
    }
    result = col("quiz_attempts").insert_one(attempt)
    attempt["_id"] = result.inserted_id
    return jsonify({
        "message": "Nộp bài thành công!",
        "attempt": attempt_to_dict(attempt, include_details=True),
    }), 201


@quizzes_bp.route("/attempts/<attempt_id>", methods=["GET"])
def get_attempt_public(attempt_id):
    doc = col("quiz_attempts").find_one({"_id": parse_oid(attempt_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy bài làm"}), 404
    return jsonify(attempt_to_dict(doc, include_details=True))


# ── Admin ───────────────────────────────────────────────

@quizzes_bp.route("/admin", methods=["GET"])
@jwt_required()
def admin_list_quizzes():
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    docs = list(col("quizzes").find().sort("created_at", -1))
    out = []
    for d in docs:
        item = quiz_to_dict(d, include_answers=False)
        item["questions"] = []
        item["attempt_count"] = col("quiz_attempts").count_documents({"quiz_id": str(d["_id"])})
        out.append(item)
    return jsonify(out)


@quizzes_bp.route("/admin", methods=["POST"])
@jwt_required()
def admin_create_quiz():
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"message": "Vui lòng nhập tên bài kiểm tra"}), 400

    try:
        questions = sanitize_questions(data.get("questions") or [])
    except ValueError as e:
        return jsonify({"message": str(e)}), 400

    now = datetime.utcnow()
    doc = {
        "title": title,
        "description": (data.get("description") or "").strip(),
        "slug": _unique_slug(),
        "duration_minutes": max(0, int(data.get("duration_minutes") or 0)),
        "is_active": bool(data.get("is_active", True)),
        "questions": questions,
        "created_at": now,
        "updated_at": now,
    }
    result = col("quizzes").insert_one(doc)
    doc["_id"] = result.inserted_id
    return jsonify(quiz_to_dict(doc, include_answers=True)), 201


@quizzes_bp.route("/admin/<quiz_id>", methods=["GET"])
@jwt_required()
def admin_get_quiz(quiz_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    doc = col("quizzes").find_one({"_id": parse_oid(quiz_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy bài kiểm tra"}), 404
    return jsonify(quiz_to_dict(doc, include_answers=True))


@quizzes_bp.route("/admin/<quiz_id>", methods=["PUT"])
@jwt_required()
def admin_update_quiz(quiz_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    doc = col("quizzes").find_one({"_id": parse_oid(quiz_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy bài kiểm tra"}), 404

    data = request.get_json() or {}
    updates = {"updated_at": datetime.utcnow()}

    if "title" in data:
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"message": "Tên bài không được trống"}), 400
        updates["title"] = title
    if "description" in data:
        updates["description"] = (data.get("description") or "").strip()
    if "duration_minutes" in data:
        updates["duration_minutes"] = max(0, int(data.get("duration_minutes") or 0))
    if "is_active" in data:
        updates["is_active"] = bool(data.get("is_active"))
    if "questions" in data:
        try:
            updates["questions"] = sanitize_questions(data.get("questions") or [])
        except ValueError as e:
            return jsonify({"message": str(e)}), 400

    col("quizzes").update_one({"_id": doc["_id"]}, {"$set": updates})
    doc = col("quizzes").find_one({"_id": doc["_id"]})
    return jsonify(quiz_to_dict(doc, include_answers=True))


@quizzes_bp.route("/admin/<quiz_id>", methods=["DELETE"])
@jwt_required()
def admin_delete_quiz(quiz_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    oid = parse_oid(quiz_id)
    doc = col("quizzes").find_one({"_id": oid})
    if not doc:
        return jsonify({"message": "Không tìm thấy bài kiểm tra"}), 404
    col("quiz_attempts").delete_many({"quiz_id": str(oid)})
    col("quizzes").delete_one({"_id": oid})
    return jsonify({"message": "Đã xóa bài kiểm tra và các bài làm liên quan"})


@quizzes_bp.route("/upload-answer-file", methods=["POST"])
def upload_answer_file():
    """Học sinh upload file đáp án (thường .sb3) trong lúc làm bài."""
    f = request.files.get("file")
    if not f or not f.filename:
        return jsonify({"message": "Chưa chọn file"}), 400

    name = (request.form.get("student_name") or "hoc_sinh").strip()
    phone = (request.form.get("phone") or "quiz").strip().replace(" ", "") or "quiz"
    filename = secure_filename(f.filename) or f.filename
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    allowed = current_app.config.get("ALLOWED_SUBMISSION_EXTENSIONS") or {"sb3", "sb2"}
    if ext not in allowed:
        return jsonify({
            "message": f"File không được hỗ trợ. Cho phép: {', '.join(sorted(allowed))}",
        }), 400

    try:
        meta = upload_submission_file(f, name, phone)
    except Exception as exc:
        return jsonify({"message": f"Upload thất bại: {exc}"}), 500
    return jsonify(meta)


@quizzes_bp.route("/admin/upload-image", methods=["POST"])
@jwt_required()
def admin_upload_image():
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    f = request.files.get("file") or request.files.get("image")
    if not f or not f.filename:
        return jsonify({"message": "Chưa chọn ảnh"}), 400
    ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
    if ext not in current_app.config.get("ALLOWED_EXTENSIONS", set()):
        return jsonify({"message": "Chỉ chấp nhận ảnh png/jpg/jpeg/gif/webp"}), 400
    try:
        meta = upload_image_file(f, folder="quiz_images")
    except Exception as exc:
        return jsonify({"message": f"Upload ảnh thất bại: {exc}"}), 500
    return jsonify(meta)


@quizzes_bp.route("/admin/<quiz_id>/attempts", methods=["GET"])
@jwt_required()
def admin_list_attempts(quiz_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    docs = col("quiz_attempts").find({"quiz_id": str(quiz_id)}).sort("submitted_at", -1)
    return jsonify([attempt_to_dict(d) for d in docs])


@quizzes_bp.route("/admin/attempts/<attempt_id>", methods=["GET"])
@jwt_required()
def admin_get_attempt(attempt_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    doc = col("quiz_attempts").find_one({"_id": parse_oid(attempt_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy bài làm"}), 404
    return jsonify(attempt_to_dict(doc, include_details=True))


@quizzes_bp.route("/admin/attempts/<attempt_id>", methods=["DELETE"])
@jwt_required()
def admin_delete_attempt(attempt_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    result = col("quiz_attempts").delete_one({"_id": parse_oid(attempt_id)})
    if result.deleted_count == 0:
        return jsonify({"message": "Không tìm thấy bài làm"}), 404
    return jsonify({"message": "Đã xóa bài làm"})


@quizzes_bp.route("/admin/attempts/<attempt_id>/grade-code", methods=["POST"])
@jwt_required()
def admin_grade_code(attempt_id):
    """Chấm thủ công câu python_code / scratch_file: { question_id, points_awarded }."""
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    doc = col("quiz_attempts").find_one({"_id": parse_oid(attempt_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy bài làm"}), 404
    data = request.get_json() or {}
    qid = str(data.get("question_id") or "")
    try:
        awarded = int(data.get("points_awarded"))
    except (TypeError, ValueError):
        return jsonify({"message": "Điểm không hợp lệ"}), 400

    details = list(doc.get("details") or [])
    found = False
    for d in details:
        if str(d.get("question_id")) != qid:
            continue
        if d.get("type") not in ("python_code", "scratch_file"):
            return jsonify({"message": "Chỉ chấm được câu tự luận / nộp file Scratch"}), 400
        max_pts = int(d.get("points") or 0)
        awarded = max(0, min(awarded, max_pts))
        d["points_awarded"] = awarded
        d["needs_manual_review"] = False
        if awarded >= max_pts:
            d["is_correct"] = True
        elif awarded <= 0:
            d["is_correct"] = False
        else:
            d["is_correct"] = None  # đúng một phần
        found = True
        break
    if not found:
        return jsonify({"message": "Không tìm thấy câu hỏi"}), 404

    earned, max_score, score, pending = recompute_attempt_score(details)
    col("quiz_attempts").update_one(
        {"_id": doc["_id"]},
        {"$set": {
            "details": details,
            "earned": earned,
            "max_score": max_score,
            "score": score,
            "pending_manual": pending,
        }},
    )
    doc = col("quiz_attempts").find_one({"_id": doc["_id"]})
    return jsonify(attempt_to_dict(doc, include_details=True))


@quizzes_bp.route("/admin/<quiz_id>/export", methods=["GET"])
@jwt_required()
def admin_export_attempts(quiz_id):
    """Xuất Excel: mỗi lớp 1 sheet — tên, điểm, link chi tiết bài làm."""
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    quiz = col("quizzes").find_one({"_id": parse_oid(quiz_id)})
    if not quiz:
        return jsonify({"message": "Không tìm thấy bài kiểm tra"}), 404

    attempts = list(col("quiz_attempts").find({"quiz_id": str(quiz["_id"])}).sort("submitted_at", -1))
    frontend = (current_app.config.get("FRONTEND_URL") or "https://kiemtradauvao.vercel.app").rstrip("/")
    quiz_oid = oid_str(quiz["_id"])

    def _sheet_name(raw):
        name = (raw or "").strip() or "Khong_ro_lop"
        for ch in r'\/?*[]:':
            name = name.replace(ch, "_")
        return name[:31] or "Khong_ro_lop"

    def _sort_key(grade):
        g = (grade or "").strip()
        order = {
            "Scratch1": 0, "Scratch2": 1, "Scratch3": 2, "Scratch4": 3,
            "Scratch 1": 0, "Scratch 2": 1, "Scratch 3": 2, "Scratch 4": 3,
        }
        if g in order:
            return (0, order[g], g.lower())
        if not g or g == "Không rõ lớp":
            return (2, 99, "")
        return (1, 0, g.lower())

    by_grade = {}
    for a in attempts:
        grade = (a.get("student_grade") or "").strip() or "Không rõ lớp"
        by_grade.setdefault(grade, []).append(a)

    grades_sorted = sorted(by_grade.keys(), key=_sort_key)

    wb = Workbook()
    default_ws = wb.active
    wb.remove(default_ws)

    header_fill = PatternFill("solid", fgColor="4A90D9")
    header_font = Font(bold=True, color="FFFFFF")
    link_font = Font(color="0563C1", underline="single")
    headers = [
        "STT",
        "Ten hoc sinh",
        "Diem %",
        "Diem (dat/tong)",
        "Link chi tiet bai lam",
        "Link admin cham bai",
        "Ngay nop",
    ]

    used_titles = set()

    def _unique_title(base):
        title = base
        n = 2
        while title in used_titles:
            suffix = f"_{n}"
            title = base[: 31 - len(suffix)] + suffix
            n += 1
        used_titles.add(title)
        return title

    def _fill_sheet(ws, rows):
        ws.append(headers)
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(1, col_idx)
            cell.fill = header_fill
            cell.font = header_font
        for i, a in enumerate(rows, 1):
            attempt_id = oid_str(a["_id"])
            detail_url = f"{frontend}/quiz-ket-qua/{attempt_id}"
            admin_url = f"{frontend}/admin/quizzes/{quiz_oid}/results?attempt={attempt_id}"
            submitted = a.get("submitted_at")
            date_str = (
                submitted.strftime("%d/%m/%Y %H:%M")
                if hasattr(submitted, "strftime")
                else str(submitted or "")
            )
            ws.append([
                i,
                a.get("student_name") or "",
                a.get("score"),
                f"{a.get('earned')}/{a.get('max_score')}",
                "Xem chi tiet",
                "Cham bai",
                date_str,
            ])
            row = ws.max_row
            c_detail = ws.cell(row, 5)
            c_detail.hyperlink = detail_url
            c_detail.font = link_font
            c_admin = ws.cell(row, 6)
            c_admin.hyperlink = admin_url
            c_admin.font = link_font
        ws.column_dimensions["A"].width = 6
        ws.column_dimensions["B"].width = 28
        ws.column_dimensions["C"].width = 10
        ws.column_dimensions["D"].width = 14
        ws.column_dimensions["E"].width = 18
        ws.column_dimensions["F"].width = 18
        ws.column_dimensions["G"].width = 18

    ws_all = wb.create_sheet(_unique_title("Tat_ca"), 0)
    _fill_sheet(ws_all, attempts)

    for grade in grades_sorted:
        ws = wb.create_sheet(_unique_title(_sheet_name(grade)))
        rows = sorted(by_grade[grade], key=lambda x: (x.get("student_name") or "").lower())
        _fill_sheet(ws, rows)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in (quiz.get("title") or "quiz"))[:40]
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"ket_qua_{safe_title}.xlsx",
    )
