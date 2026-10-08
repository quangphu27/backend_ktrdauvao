"""Phát trực tiếp lớp học — admin mở camera/mic, học sinh xem tại /lophoc (WebRTC PeerJS)."""

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from database import col

live_bp = Blueprint("live", __name__, url_prefix="/api/live")

ROOM_ID = "lophoc"


def _admin_required():
    return get_jwt().get("role") == "admin"


def _doc():
    return col("live_classroom").find_one({"room": ROOM_ID}) or {
        "room": ROOM_ID,
        "live": False,
        "peer_id": None,
        "viewer_count_hint": 0,
        "started_at": None,
        "started_by": None,
    }


def _public(doc):
    return {
        "room": ROOM_ID,
        "live": bool(doc.get("live")),
        "peer_id": doc.get("peer_id") if doc.get("live") else None,
        "started_at": (
            doc["started_at"].isoformat() + "Z"
            if isinstance(doc.get("started_at"), datetime)
            else doc.get("started_at")
        ),
        "started_by": doc.get("started_by"),
    }


@live_bp.route("/status", methods=["GET"])
def live_status():
    """Công khai — học sinh poll để biết đang phát + peer_id."""
    return jsonify(_public(_doc()))


@live_bp.route("/start", methods=["POST"])
@jwt_required()
def live_start():
    """Admin: báo đang phát. Body: { peer_id }."""
    if not _admin_required():
        return jsonify({"message": "Không có quyền"}), 403

    data = request.get_json(silent=True) or {}
    peer_id = (data.get("peer_id") or "").strip()
    if not peer_id:
        return jsonify({"message": "Thiếu peer_id"}), 400

    claims = get_jwt()
    now = datetime.utcnow()
    col("live_classroom").update_one(
        {"room": ROOM_ID},
        {
            "$set": {
                "room": ROOM_ID,
                "live": True,
                "peer_id": peer_id,
                "started_at": now,
                "started_by": claims.get("sub") or claims.get("email") or "admin",
                "updated_at": now,
            }
        },
        upsert=True,
    )
    return jsonify(_public(_doc()))


@live_bp.route("/stop", methods=["POST"])
@jwt_required()
def live_stop():
    """Admin: dừng phát."""
    if not _admin_required():
        return jsonify({"message": "Không có quyền"}), 403

    now = datetime.utcnow()
    col("live_classroom").update_one(
        {"room": ROOM_ID},
        {
            "$set": {
                "live": False,
                "peer_id": None,
                "stopped_at": now,
                "updated_at": now,
            }
        },
        upsert=True,
    )
    return jsonify(_public(_doc()))
