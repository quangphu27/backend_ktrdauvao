"""API chat học sinh ↔ admin."""

from __future__ import annotations

import time
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from database import col, parse_oid
from models import user_to_dict
from services import chat_service as chat

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


def _current_user():
    uid = get_jwt_identity()
    doc = col("users").find_one({"_id": parse_oid(uid)})
    if not doc:
        return None
    return user_to_dict(doc)


def _require_user():
    user = _current_user()
    if not user:
        return None, (jsonify({"message": "Không tìm thấy người dùng"}), 404)
    return user, None


_INDEXES_READY = False


def _ready_indexes():
    global _INDEXES_READY
    if _INDEXES_READY:
        return
    try:
        chat.ensure_indexes()
        _INDEXES_READY = True
    except Exception:
        pass


@chat_bp.route("/me/thread", methods=["GET"])
@jwt_required()
def my_thread():
    _ready_indexes()
    user, err = _require_user()
    if err:
        return err
    if user.get("role") == "admin":
        return jsonify({"message": "Admin dùng /api/chat/admin/threads"}), 400
    thread = chat.get_or_create_student_thread(user)
    return jsonify(chat.thread_to_dict(thread))


@chat_bp.route("/me/messages", methods=["GET"])
@jwt_required()
def my_messages():
    _ready_indexes()
    user, err = _require_user()
    if err:
        return err
    if user.get("role") == "admin":
        return jsonify({"message": "Admin dùng endpoint admin"}), 400

    thread = chat.get_or_create_student_thread(user)
    after = request.args.get("after")
    before = request.args.get("before")
    limit = request.args.get("limit", type=int) or 50
    msgs = chat.list_messages(str(thread["_id"]), after=after, before=before, limit=limit)
    chat.mark_read(thread=thread, reader_role="student")
    refreshed = chat.get_thread(str(thread["_id"]))
    return jsonify({
        "thread": chat.thread_to_dict(refreshed or thread),
        "messages": msgs,
    })


@chat_bp.route("/me/messages", methods=["POST"])
@jwt_required()
def send_my_message():
    _ready_indexes()
    user, err = _require_user()
    if err:
        return err
    if user.get("role") == "admin":
        return jsonify({"message": "Admin dùng endpoint admin"}), 400

    data = request.get_json(silent=True) or {}
    thread = chat.get_or_create_student_thread(user)
    try:
        msg = chat.post_message(
            thread=thread,
            sender_id=user["id"],
            sender_role="student",
            sender_name=user.get("full_name") or "",
            text=data.get("text") or "",
        )
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    refreshed = chat.get_thread(str(thread["_id"]))
    return jsonify({"message": msg, "thread": chat.thread_to_dict(refreshed)}), 201


@chat_bp.route("/admin/threads", methods=["GET"])
@jwt_required()
def admin_threads():
    _ready_indexes()
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"message": "Không có quyền"}), 403
    return jsonify(chat.list_admin_threads())


@chat_bp.route("/admin/threads/<thread_id>/messages", methods=["GET"])
@jwt_required()
def admin_thread_messages(thread_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"message": "Không có quyền"}), 403
    thread = chat.get_thread(thread_id)
    if not thread:
        return jsonify({"message": "Không tìm thấy hội thoại"}), 404
    after = request.args.get("after")
    before = request.args.get("before")
    limit = request.args.get("limit", type=int) or 50
    msgs = chat.list_messages(thread_id, after=after, before=before, limit=limit)
    chat.mark_read(thread=thread, reader_role="admin")
    refreshed = chat.get_thread(thread_id)
    return jsonify({
        "thread": chat.thread_to_dict(refreshed or thread),
        "messages": msgs,
    })


@chat_bp.route("/admin/threads/<thread_id>/messages", methods=["POST"])
@jwt_required()
def admin_send_message(thread_id):
    user, err = _require_user()
    if err:
        return err
    if user.get("role") != "admin":
        return jsonify({"message": "Không có quyền"}), 403
    thread = chat.get_thread(thread_id)
    if not thread:
        return jsonify({"message": "Không tìm thấy hội thoại"}), 404
    data = request.get_json(silent=True) or {}
    try:
        msg = chat.post_message(
            thread=thread,
            sender_id=user["id"],
            sender_role="admin",
            sender_name=user.get("full_name") or "Admin",
            text=data.get("text") or "",
        )
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    refreshed = chat.get_thread(thread_id)
    return jsonify({"message": msg, "thread": chat.thread_to_dict(refreshed)}), 201


@chat_bp.route("/updates", methods=["GET"])
@jwt_required()
def chat_updates():
    """Long-poll gần realtime: chờ tin mới tối đa ~25s."""
    _ready_indexes()
    user, err = _require_user()
    if err:
        return err

    since_raw = (request.args.get("since") or "").strip()
    thread_id = (request.args.get("thread_id") or "").strip() or None
    # Mặc định wait=0 (short-poll): Render/gunicorn 1 worker sẽ bị treo nếu long-poll
    wait = request.args.get("wait", type=int)
    if wait is None:
        wait = 0
    wait = max(0, min(wait, 15))

    if since_raw:
        try:
            since = datetime.fromisoformat(since_raw.replace("Z", ""))
        except ValueError:
            since = datetime.utcnow()
    else:
        since = datetime.utcnow()

    role = "admin" if user.get("role") == "admin" else "student"
    deadline = time.time() + wait
    while True:
        payload = chat.poll_updates(
            role=role,
            user_id=user["id"],
            since=since,
            thread_id=thread_id if role == "admin" else None,
        )
        if payload["messages"] or wait <= 0:
            return jsonify(payload)
        if time.time() >= deadline:
            return jsonify(payload)
        time.sleep(1.2)
