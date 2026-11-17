"""API Scratch Arena — namespace độc lập /api/scratch-arena/"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from services.scratch_arena import session_service as svc

scratch_arena_bp = Blueprint("scratch_arena", __name__, url_prefix="/api/scratch-arena")


def _optional_user_id():
    try:
        verify_jwt_in_request(optional=True)
        return get_jwt_identity()
    except Exception:
        return None


@scratch_arena_bp.get("/health")
def health():
    return jsonify({"status": "ok", "module": "scratch-arena"})


@scratch_arena_bp.get("/questions")
def questions():
    limit = min(20, max(1, int(request.args.get("limit") or 8)))
    public, _key = svc.fetch_warmup_questions(limit)
    return jsonify({"questions": public})


@scratch_arena_bp.get("/challenges")
def challenges():
    round_num = request.args.get("round")
    rn = int(round_num) if round_num not in (None, "") else None
    return jsonify({"challenges": svc.list_challenges(rn)})


@scratch_arena_bp.post("/sessions")
def create_session():
    data = request.get_json(silent=True) or {}
    name = (data.get("player_name") or data.get("name") or "Thí sinh").strip()
    difficulty = (data.get("difficulty") or "medium").strip().lower()
    if difficulty not in ("easy", "medium", "hard"):
        difficulty = "medium"
    if len(name) > 40:
        name = name[:40]
    user_id = _optional_user_id()
    doc, questions = svc.create_session(name, difficulty, user_id=user_id)
    return jsonify({
        "session": svc.public_session(doc),
        "questions": questions,
        "ai_profiles": {
            "easy": {"buzz_ms": [1800, 3200], "accuracy": 0.55},
            "medium": {"buzz_ms": [900, 1800], "accuracy": 0.72},
            "hard": {"buzz_ms": [450, 1100], "accuracy": 0.88},
        },
    }), 201


@scratch_arena_bp.get("/sessions/<session_id>")
def get_session(session_id):
    doc = svc.get_session(session_id)
    if not doc:
        return jsonify({"error": "Không tìm thấy phiên"}), 404
    return jsonify({"session": svc.public_session(doc)})


@scratch_arena_bp.post("/sessions/<session_id>/buzz")
def buzz(session_id):
    data = request.get_json(silent=True) or {}
    player_id = (data.get("player_id") or "human").strip()
    question_id = (data.get("question_id") or "").strip()
    if not question_id:
        return jsonify({"error": "Thiếu question_id"}), 400
    client_ms = data.get("client_ms")
    try:
        client_ms = int(client_ms) if client_ms is not None else None
    except Exception:
        client_ms = None
    result, err = svc.record_buzz(session_id, player_id, question_id, client_ms)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(result)


@scratch_arena_bp.post("/sessions/<session_id>/answer")
def answer(session_id):
    data = request.get_json(silent=True) or {}
    player_id = (data.get("player_id") or "human").strip()
    question_id = (data.get("question_id") or "").strip()
    option_id = (data.get("option_id") or "").strip()
    if not question_id or not option_id:
        return jsonify({"error": "Thiếu question_id hoặc option_id"}), 400
    # Chỉ cho phép human nộp qua endpoint này; AI dùng /ai-score sau khi client mô phỏng
    if player_id != "human":
        return jsonify({"error": "Dùng endpoint AI riêng"}), 400
    result, err = svc.grade_warmup_answer(session_id, question_id, player_id, option_id)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(result)


@scratch_arena_bp.post("/sessions/<session_id>/ai-score")
def ai_score(session_id):
    """Cộng điểm AI có kiểm soát (player_id phải là ai_*)."""
    data = request.get_json(silent=True) or {}
    player_id = (data.get("player_id") or "").strip()
    points = data.get("points")
    try:
        points = int(points)
    except Exception:
        return jsonify({"error": "points không hợp lệ"}), 400
    scores = svc.apply_ai_score(session_id, player_id, points)
    if scores is None:
        return jsonify({"error": "Không cộng điểm AI"}), 400
    return jsonify({"scores": scores})


@scratch_arena_bp.post("/sessions/<session_id>/submit")
def submit(session_id):
    data = request.get_json(silent=True) or {}
    player_id = (data.get("player_id") or "human").strip()
    slug = (data.get("challenge_slug") or data.get("slug") or "").strip()
    payload = data.get("payload") or {}
    if player_id != "human":
        return jsonify({"error": "Chỉ thí sinh người nộp qua API này"}), 400
    if not slug:
        return jsonify({"error": "Thiếu challenge_slug"}), 400
    result, err = svc.grade_challenge_submit(session_id, slug, player_id, payload)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(result)


@scratch_arena_bp.post("/sessions/<session_id>/round")
def set_round(session_id):
    data = request.get_json(silent=True) or {}
    try:
        rn = int(data.get("round"))
    except Exception:
        return jsonify({"error": "round không hợp lệ"}), 400
    if rn < 1 or rn > 4:
        return jsonify({"error": "round phải 1–4"}), 400
    doc = svc.set_round(session_id, rn)
    if not doc:
        return jsonify({"error": "Không tìm thấy phiên"}), 404
    return jsonify({"session": svc.public_session(doc)})


@scratch_arena_bp.post("/sessions/<session_id>/finish")
def finish(session_id):
    result, err = svc.finish_session(session_id)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(result)


@scratch_arena_bp.get("/leaderboard")
def leaderboard():
    limit = min(50, max(1, int(request.args.get("limit") or 20)))
    return jsonify({"leaderboard": svc.leaderboard(limit)})
