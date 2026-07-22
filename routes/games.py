"""API trò chơi: ô chữ bí mật, ai nhanh hơn, đuổi hình bắt chữ."""

from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from database import col, parse_oid
from services.cloudinary_service import upload_image_file
from services.game_service import (
    check_option_correct,
    crossword_to_dict,
    fast_quiz_to_dict,
    generate_slug,
    new_id,
    normalize_letters,
    picture_word_to_dict,
    sanitize_crossword_payload,
    sanitize_fast_quiz,
    sanitize_picture_word,
)

games_bp = Blueprint("games", __name__, url_prefix="/api/games")


def _admin_required():
    return get_jwt().get("role") == "admin"


def _unique_slug(collection):
    for _ in range(20):
        slug = generate_slug()
        if not col(collection).find_one({"slug": slug}):
            return slug
    return generate_slug(12)


def _find_player(players, player_id):
    for p in players or []:
        if str(p.get("id")) == str(player_id):
            return p
    return None


@games_bp.route("/admin/upload-image", methods=["POST"])
@jwt_required()
def upload_image():
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    f = request.files.get("file") or request.files.get("image")
    if not f or not f.filename:
        return jsonify({"message": "Chưa chọn ảnh"}), 400
    ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
    if ext not in current_app.config.get("ALLOWED_EXTENSIONS", set()):
        return jsonify({"message": "Chỉ chấp nhận ảnh png/jpg/jpeg/gif/webp"}), 400
    try:
        meta = upload_image_file(f, folder="game_images")
    except Exception as exc:
        return jsonify({"message": f"Upload thất bại: {exc}"}), 500
    return jsonify(meta)


@games_bp.route("/admin", methods=["GET"])
@jwt_required()
def admin_list_all():
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    items = []
    for d in col("crossword_games").find().sort("created_at", -1):
        item = crossword_to_dict(d, include_answers=False)
        item["row_count"] = len(d.get("rows") or [])
        items.append(item)
    for d in col("fast_quiz_games").find().sort("created_at", -1):
        item = fast_quiz_to_dict(d, include_answers=False)
        item["question_count"] = len(d.get("questions") or [])
        items.append(item)
    for d in col("picture_word_games").find().sort("created_at", -1):
        item = picture_word_to_dict(d, include_answers=False)
        item["round_count"] = len(d.get("rounds") or [])
        items.append(item)
    items.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return jsonify(items)


# ── Crossword ───────────────────────────────────────────

@games_bp.route("/admin/crossword", methods=["POST"])
@jwt_required()
def create_crossword():
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    try:
        payload = sanitize_crossword_payload(request.get_json() or {})
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    now = datetime.utcnow()
    doc = {
        **payload,
        "slug": _unique_slug("crossword_games"),
        "players": [],
        "solved_rows": [],
        "failed_rows": [],
        "vertical_solved": False,
        "vertical_failed": False,
        "wrong_options": {},
        "created_at": now,
        "updated_at": now,
    }
    result = col("crossword_games").insert_one(doc)
    doc["_id"] = result.inserted_id
    return jsonify(crossword_to_dict(doc, include_answers=True)), 201


@games_bp.route("/admin/crossword/<game_id>", methods=["GET"])
@jwt_required()
def get_crossword_admin(game_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    doc = col("crossword_games").find_one({"_id": parse_oid(game_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy trò chơi"}), 404
    return jsonify(crossword_to_dict(doc, include_answers=True))


@games_bp.route("/admin/crossword/<game_id>", methods=["PUT"])
@jwt_required()
def update_crossword(game_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    doc = col("crossword_games").find_one({"_id": parse_oid(game_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy trò chơi"}), 404
    data = request.get_json() or {}
    try:
        payload = sanitize_crossword_payload({
            "title": data.get("title", doc.get("title")),
            "description": data.get("description", doc.get("description")),
            "rows": data.get("rows", doc.get("rows")),
            "vertical_answer": data.get("vertical_answer", doc.get("vertical_answer")),
            "vertical_question": data.get("vertical_question", doc.get("vertical_question")),
            "is_active": data.get("is_active", doc.get("is_active", True)),
        })
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    payload["updated_at"] = datetime.utcnow()
    # Giữ trạng thái chơi / người chơi
    col("crossword_games").update_one({"_id": doc["_id"]}, {"$set": payload})
    doc = col("crossword_games").find_one({"_id": doc["_id"]})
    return jsonify(crossword_to_dict(doc, include_answers=True))


@games_bp.route("/admin/crossword/<game_id>", methods=["DELETE"])
@jwt_required()
def delete_crossword(game_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    result = col("crossword_games").delete_one({"_id": parse_oid(game_id)})
    if result.deleted_count == 0:
        return jsonify({"message": "Không tìm thấy trò chơi"}), 404
    return jsonify({"message": "Đã xóa trò chơi"})


@games_bp.route("/admin/crossword/<game_id>/reset", methods=["POST"])
@jwt_required()
def reset_crossword(game_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    doc = col("crossword_games").find_one({"_id": parse_oid(game_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy trò chơi"}), 404
    players = [
        {**p, "score": 0}
        for p in (doc.get("players") or [])
    ]
    col("crossword_games").update_one(
        {"_id": doc["_id"]},
        {"$set": {
            "solved_rows": [],
            "failed_rows": [],
            "vertical_solved": False,
            "vertical_failed": False,
            "wrong_options": {},
            "players": players,
            "updated_at": datetime.utcnow(),
        }},
    )
    doc = col("crossword_games").find_one({"_id": doc["_id"]})
    return jsonify(crossword_to_dict(doc, include_answers=True))


@games_bp.route("/admin/<game_type>/<game_id>/players", methods=["POST"])
@jwt_required()
def add_player(game_type, game_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    collection = {
        "crossword": "crossword_games",
        "fast_quiz": "fast_quiz_games",
        "picture_word": "picture_word_games",
    }.get(game_type)
    if not collection:
        return jsonify({"message": "Loại trò chơi không hợp lệ"}), 400
    doc = col(collection).find_one({"_id": parse_oid(game_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy trò chơi"}), 404
    name = ((request.get_json() or {}).get("name") or "").strip()
    if not name:
        return jsonify({"message": "Nhập tên người chơi"}), 400
    player = {"id": new_id(), "name": name, "score": 0}
    col(collection).update_one({"_id": doc["_id"]}, {"$push": {"players": player}})
    return jsonify(player), 201


@games_bp.route("/admin/<game_type>/<game_id>/players/<player_id>", methods=["DELETE"])
@jwt_required()
def delete_player(game_type, game_id, player_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    collection = {
        "crossword": "crossword_games",
        "fast_quiz": "fast_quiz_games",
        "picture_word": "picture_word_games",
    }.get(game_type)
    if not collection:
        return jsonify({"message": "Loại trò chơi không hợp lệ"}), 400
    result = col(collection).update_one(
        {"_id": parse_oid(game_id)},
        {"$pull": {"players": {"id": player_id}}},
    )
    if result.matched_count == 0:
        return jsonify({"message": "Không tìm thấy trò chơi"}), 404
    return jsonify({"message": "Đã xóa người chơi"})


@games_bp.route("/admin/<game_type>/<game_id>/players/<player_id>/score", methods=["POST"])
@jwt_required()
def adjust_score(game_type, game_id, player_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    collection = {
        "crossword": "crossword_games",
        "fast_quiz": "fast_quiz_games",
        "picture_word": "picture_word_games",
    }.get(game_type)
    if not collection:
        return jsonify({"message": "Loại trò chơi không hợp lệ"}), 400
    doc = col(collection).find_one({"_id": parse_oid(game_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy trò chơi"}), 404
    data = request.get_json() or {}
    delta = int(data.get("delta") or 0)
    absolute = data.get("score")
    players = doc.get("players") or []
    found = False
    for p in players:
        if str(p.get("id")) == str(player_id):
            if absolute is not None:
                p["score"] = int(absolute)
            else:
                p["score"] = int(p.get("score") or 0) + delta
            found = True
            break
    if not found:
        return jsonify({"message": "Không tìm thấy người chơi"}), 404
    col(collection).update_one({"_id": doc["_id"]}, {"$set": {"players": players}})
    return jsonify({"players": players})


def _winners(players):
    if not players:
        return []
    best = max(int(p.get("score") or 0) for p in players)
    return [
        {"id": p.get("id"), "name": p.get("name"), "score": int(p.get("score") or 0)}
        for p in players
        if int(p.get("score") or 0) == best
    ]


# ── Crossword play (public by slug, admin can also use) ─

@games_bp.route("/crossword/<slug>", methods=["GET"])
def get_crossword_play(slug):
    doc = col("crossword_games").find_one({"slug": slug, "is_active": True})
    if not doc:
        return jsonify({"message": "Không tìm thấy trò chơi"}), 404
    data = crossword_to_dict(doc, include_answers=False)
    # Reveal letters for solved rows only
    revealed = {}
    for rid in doc.get("solved_rows") or []:
        row = next((r for r in doc.get("rows") or [] if r["id"] == rid), None)
        if row:
            revealed[rid] = row.get("answer")
    data["revealed_rows"] = revealed
    data["failed_rows"] = doc.get("failed_rows") or []
    data["vertical_solved"] = bool(doc.get("vertical_solved"))
    data["vertical_failed"] = bool(doc.get("vertical_failed"))
    if doc.get("vertical_solved"):
        data["vertical_answer"] = doc.get("vertical_answer")
    data["wrong_options"] = doc.get("wrong_options") or {}
    data["players"] = doc.get("players") or []
    if doc.get("vertical_solved") or doc.get("vertical_failed"):
        data["winners"] = _winners(doc.get("players") or [])
        data["game_finished"] = True
    else:
        data["winners"] = []
        data["game_finished"] = False
    return jsonify(data)


@games_bp.route("/crossword/<slug>/answer-row", methods=["POST"])
def answer_crossword_row(slug):
    doc = col("crossword_games").find_one({"slug": slug, "is_active": True})
    if not doc:
        return jsonify({"message": "Không tìm thấy trò chơi"}), 404
    data = request.get_json() or {}
    row_id = data.get("row_id")
    option_id = data.get("option_id")
    player_id = data.get("player_id")
    row = next((r for r in doc.get("rows") or [] if r["id"] == row_id), None)
    if not row:
        return jsonify({"message": "Không tìm thấy hàng"}), 404
    if row_id in (doc.get("solved_rows") or []):
        return jsonify({"message": "Hàng này đã mở rồi", "already_solved": True}), 400
    if row_id in (doc.get("failed_rows") or []):
        return jsonify({"message": "Hàng này đã trả lời sai rồi", "already_failed": True}), 400

    correct, _ = check_option_correct(row.get("question"), option_id)
    wrong_options = doc.get("wrong_options") or {}

    if not correct:
        failed = list(doc.get("failed_rows") or [])
        if row_id not in failed:
            failed.append(row_id)
        if option_id:
            wrong_options[row_id] = [str(option_id)]
        col("crossword_games").update_one(
            {"_id": doc["_id"]},
            {"$set": {
                "failed_rows": failed,
                "wrong_options": wrong_options,
                "updated_at": datetime.utcnow(),
            }},
        )
        return jsonify({
            "correct": False,
            "locked": True,
            "failed_rows": failed,
            "wrong_options": wrong_options.get(row_id) or [],
            "message": "Sai rồi! Câu này không chọn lại được.",
        })

    solved = list(doc.get("solved_rows") or [])
    solved.append(row_id)
    players = doc.get("players") or []
    points = int(row.get("points") or 10)
    if player_id:
        p = _find_player(players, player_id)
        if p:
            p["score"] = int(p.get("score") or 0) + points
    col("crossword_games").update_one(
        {"_id": doc["_id"]},
        {"$set": {
            "solved_rows": solved,
            "players": players,
            "wrong_options": wrong_options,
            "updated_at": datetime.utcnow(),
        }},
    )
    return jsonify({
        "correct": True,
        "answer": row.get("answer"),
        "points": points,
        "players": players,
        "solved_rows": solved,
        "message": f"Đúng rồi! +{points} điểm",
    })


@games_bp.route("/crossword/<slug>/answer-vertical", methods=["POST"])
def answer_crossword_vertical(slug):
    doc = col("crossword_games").find_one({"slug": slug, "is_active": True})
    if not doc:
        return jsonify({"message": "Không tìm thấy trò chơi"}), 404
    if doc.get("vertical_solved"):
        return jsonify({"message": "Ô chữ dọc đã mở rồi", "already_solved": True}), 400
    if doc.get("vertical_failed"):
        return jsonify({"message": "Ô chữ dọc đã trả lời sai rồi", "already_failed": True}), 400
    data = request.get_json() or {}
    option_id = data.get("option_id")
    player_id = data.get("player_id")
    correct, _ = check_option_correct(doc.get("vertical_question"), option_id)
    wrong_options = doc.get("wrong_options") or {}
    players = doc.get("players") or []

    if not correct:
        if option_id:
            wrong_options["__vertical__"] = [str(option_id)]
        col("crossword_games").update_one(
            {"_id": doc["_id"]},
            {"$set": {
                "vertical_failed": True,
                "wrong_options": wrong_options,
                "updated_at": datetime.utcnow(),
            }},
        )
        winners = _winners(players)
        return jsonify({
            "correct": False,
            "locked": True,
            "vertical_failed": True,
            "wrong_options": wrong_options.get("__vertical__") or [],
            "players": players,
            "winners": winners,
            "game_finished": True,
            "message": "Sai ô chữ bí mật! Câu này không chọn lại được.",
        })

    points = int(doc.get("vertical_points") or 30)
    if player_id:
        p = _find_player(players, player_id)
        if p:
            p["score"] = int(p.get("score") or 0) + points
    col("crossword_games").update_one(
        {"_id": doc["_id"]},
        {"$set": {
            "vertical_solved": True,
            "players": players,
            "updated_at": datetime.utcnow(),
        }},
    )
    winners = _winners(players)
    return jsonify({
        "correct": True,
        "answer": doc.get("vertical_answer"),
        "points": points,
        "players": players,
        "winners": winners,
        "game_finished": True,
        "message": f"Mở khóa ô chữ bí mật! +{points} điểm",
    })


# ── Fast quiz ───────────────────────────────────────────

@games_bp.route("/admin/fast-quiz", methods=["POST"])
@jwt_required()
def create_fast_quiz():
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    try:
        payload = sanitize_fast_quiz(request.get_json() or {})
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    now = datetime.utcnow()
    doc = {
        **payload,
        "slug": _unique_slug("fast_quiz_games"),
        "players": [],
        "created_at": now,
        "updated_at": now,
    }
    result = col("fast_quiz_games").insert_one(doc)
    doc["_id"] = result.inserted_id
    return jsonify(fast_quiz_to_dict(doc, include_answers=True)), 201


@games_bp.route("/admin/fast-quiz/<game_id>", methods=["GET"])
@jwt_required()
def get_fast_quiz_admin(game_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    doc = col("fast_quiz_games").find_one({"_id": parse_oid(game_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy"}), 404
    return jsonify(fast_quiz_to_dict(doc, include_answers=True))


@games_bp.route("/admin/fast-quiz/<game_id>", methods=["PUT"])
@jwt_required()
def update_fast_quiz(game_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    doc = col("fast_quiz_games").find_one({"_id": parse_oid(game_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy"}), 404
    data = request.get_json() or {}
    try:
        payload = sanitize_fast_quiz({
            "title": data.get("title", doc.get("title")),
            "description": data.get("description", doc.get("description")),
            "questions": data.get("questions", doc.get("questions")),
            "is_active": data.get("is_active", doc.get("is_active", True)),
        })
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    payload["updated_at"] = datetime.utcnow()
    col("fast_quiz_games").update_one({"_id": doc["_id"]}, {"$set": payload})
    doc = col("fast_quiz_games").find_one({"_id": doc["_id"]})
    return jsonify(fast_quiz_to_dict(doc, include_answers=True))


@games_bp.route("/admin/fast-quiz/<game_id>", methods=["DELETE"])
@jwt_required()
def delete_fast_quiz(game_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    result = col("fast_quiz_games").delete_one({"_id": parse_oid(game_id)})
    if result.deleted_count == 0:
        return jsonify({"message": "Không tìm thấy"}), 404
    return jsonify({"message": "Đã xóa"})


@games_bp.route("/fast-quiz/<slug>", methods=["GET"])
def get_fast_quiz_play(slug):
    doc = col("fast_quiz_games").find_one({"slug": slug, "is_active": True})
    if not doc:
        return jsonify({"message": "Không tìm thấy trò chơi"}), 404
    data = fast_quiz_to_dict(doc, include_answers=False)
    data["players"] = doc.get("players") or []
    return jsonify(data)


@games_bp.route("/fast-quiz/<slug>/answer", methods=["POST"])
def answer_fast_quiz(slug):
    doc = col("fast_quiz_games").find_one({"slug": slug, "is_active": True})
    if not doc:
        return jsonify({"message": "Không tìm thấy trò chơi"}), 404
    data = request.get_json() or {}
    qid = data.get("question_id")
    option_id = data.get("option_id")
    player_id = data.get("player_id")
    question = next((q for q in doc.get("questions") or [] if q["id"] == qid), None)
    if not question:
        return jsonify({"message": "Không tìm thấy câu hỏi"}), 404
    correct, _ = check_option_correct(question, option_id)
    players = doc.get("players") or []
    points = int(question.get("points") or 10) if correct else 0
    if correct and player_id:
        p = _find_player(players, player_id)
        if p:
            p["score"] = int(p.get("score") or 0) + points
            col("fast_quiz_games").update_one(
                {"_id": doc["_id"]},
                {"$set": {"players": players}},
            )
    return jsonify({
        "correct": correct,
        "points": points,
        "players": players,
        "message": f"Đúng! +{points}" if correct else "Sai rồi!",
    })


# ── Picture word ────────────────────────────────────────

@games_bp.route("/admin/picture-word", methods=["POST"])
@jwt_required()
def create_picture_word():
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    try:
        payload = sanitize_picture_word(request.get_json() or {})
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    now = datetime.utcnow()
    doc = {
        **payload,
        "slug": _unique_slug("picture_word_games"),
        "players": [],
        "created_at": now,
        "updated_at": now,
    }
    result = col("picture_word_games").insert_one(doc)
    doc["_id"] = result.inserted_id
    return jsonify(picture_word_to_dict(doc, include_answers=True)), 201


@games_bp.route("/admin/picture-word/<game_id>", methods=["GET"])
@jwt_required()
def get_picture_word_admin(game_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    doc = col("picture_word_games").find_one({"_id": parse_oid(game_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy"}), 404
    return jsonify(picture_word_to_dict(doc, include_answers=True))


@games_bp.route("/admin/picture-word/<game_id>", methods=["PUT"])
@jwt_required()
def update_picture_word(game_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    doc = col("picture_word_games").find_one({"_id": parse_oid(game_id)})
    if not doc:
        return jsonify({"message": "Không tìm thấy"}), 404
    data = request.get_json() or {}
    try:
        payload = sanitize_picture_word({
            "title": data.get("title", doc.get("title")),
            "description": data.get("description", doc.get("description")),
            "rounds": data.get("rounds", doc.get("rounds")),
            "is_active": data.get("is_active", doc.get("is_active", True)),
        })
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    payload["updated_at"] = datetime.utcnow()
    col("picture_word_games").update_one({"_id": doc["_id"]}, {"$set": payload})
    doc = col("picture_word_games").find_one({"_id": doc["_id"]})
    return jsonify(picture_word_to_dict(doc, include_answers=True))


@games_bp.route("/admin/picture-word/<game_id>", methods=["DELETE"])
@jwt_required()
def delete_picture_word(game_id):
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403
    result = col("picture_word_games").delete_one({"_id": parse_oid(game_id)})
    if result.deleted_count == 0:
        return jsonify({"message": "Không tìm thấy"}), 404
    return jsonify({"message": "Đã xóa"})


@games_bp.route("/picture-word/<slug>", methods=["GET"])
def get_picture_word_play(slug):
    doc = col("picture_word_games").find_one({"slug": slug, "is_active": True})
    if not doc:
        return jsonify({"message": "Không tìm thấy trò chơi"}), 404
    data = picture_word_to_dict(doc, include_answers=False)
    data["players"] = doc.get("players") or []
    return jsonify(data)


@games_bp.route("/picture-word/<slug>/guess", methods=["POST"])
def guess_picture_word(slug):
    doc = col("picture_word_games").find_one({"slug": slug, "is_active": True})
    if not doc:
        return jsonify({"message": "Không tìm thấy trò chơi"}), 404
    data = request.get_json() or {}
    rid = data.get("round_id")
    guess = normalize_letters(data.get("guess") or "")
    player_id = data.get("player_id")
    rnd = next((r for r in doc.get("rounds") or [] if r["id"] == rid), None)
    if not rnd:
        return jsonify({"message": "Không tìm thấy vòng"}), 404
    correct = guess == rnd.get("answer")
    players = doc.get("players") or []
    points = int(rnd.get("points") or 10) if correct else 0
    if correct and player_id:
        p = _find_player(players, player_id)
        if p:
            p["score"] = int(p.get("score") or 0) + points
            col("picture_word_games").update_one(
                {"_id": doc["_id"]},
                {"$set": {"players": players}},
            )
    return jsonify({
        "correct": correct,
        "points": points,
        "answer": rnd.get("answer") if correct else None,
        "players": players,
        "message": f"Đúng! +{points}" if correct else "Chưa đúng, thử lại!",
    })
