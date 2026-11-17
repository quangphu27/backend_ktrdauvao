"""API IQ 300 — prefix /api/iq300 — độc lập với quiz cũ."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from services.iq300.catalog import public_challenges
from services.iq300 import engine

iq300_bp = Blueprint("iq300", __name__, url_prefix="/api/iq300")


def _optional_user():
    try:
        verify_jwt_in_request(optional=True)
        return get_jwt_identity()
    except Exception:
        return None


def _admin_required():
    try:
        verify_jwt_in_request()
        return get_jwt().get("role") == "admin"
    except Exception:
        return False


@iq300_bp.get("/health")
def health():
    return jsonify({"status": "ok", "module": "iq300"})


@iq300_bp.get("/challenges")
def challenges():
    return jsonify({
        "challenges": public_challenges(),
        "max_score": 150,
        "question_count": 8,
    })


@iq300_bp.post("/attempts")
def create_attempt():
    data = request.get_json(silent=True) or {}
    try:
        doc = engine.create_attempt(data, user_id=_optional_user())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({
        "attempt": engine.public_attempt(doc),
        "challenges": public_challenges(),
    }), 201


@iq300_bp.get("/attempts/<attempt_id>")
def get_attempt(attempt_id):
    doc = engine.get_attempt(attempt_id)
    if not doc:
        return jsonify({"error": "Không tìm thấy"}), 404
    finished = doc.get("status") == "finished"
    return jsonify({"attempt": engine.public_attempt(doc, include_review=finished)})


@iq300_bp.post("/attempts/<attempt_id>/weigh")
def weigh(attempt_id):
    data = request.get_json(silent=True) or {}
    result, err = engine.simulate_weigh(
        attempt_id,
        data.get("left") or [],
        data.get("right") or [],
    )
    if err:
        return jsonify({"error": err}), 400
    return jsonify(result)


@iq300_bp.post("/attempts/<attempt_id>/answer")
def answer(attempt_id):
    data = request.get_json(silent=True) or {}
    try:
        qid = int(data.get("question_id"))
    except Exception:
        return jsonify({"error": "question_id không hợp lệ"}), 400
    result, err = engine.grade_answer(
        attempt_id,
        qid,
        data.get("answer"),
        reaction_ms=data.get("reaction_ms"),
    )
    if err:
        return jsonify({"error": err}), 400
    return jsonify(result)


@iq300_bp.get("/leaderboard")
def leaderboard():
    grade = request.args.get("grade")
    return jsonify({"leaderboard": engine.leaderboard(grade=grade)})


@iq300_bp.get("/admin/attempts")
def admin_list():
    if not _admin_required():
        return jsonify({"error": "Unauthorized"}), 401
    grade = request.args.get("grade")
    limit = min(200, max(1, int(request.args.get("limit") or 100)))
    return jsonify({"attempts": engine.list_attempts(grade=grade, limit=limit)})


@iq300_bp.get("/admin/attempts/<attempt_id>")
def admin_detail(attempt_id):
    if not _admin_required():
        return jsonify({"error": "Unauthorized"}), 401
    data = engine.attempt_detail_admin(attempt_id)
    if not data:
        return jsonify({"error": "Không tìm thấy"}), 404
    return jsonify({"attempt": data})
