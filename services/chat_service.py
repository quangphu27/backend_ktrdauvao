"""Chat học sinh ↔ admin — lịch sử MongoDB + long-poll gần realtime."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from database import col, oid_str, parse_oid

MAX_TEXT = 2000
DEFAULT_LIMIT = 50


def _iso(value):
    if isinstance(value, datetime):
        return value.isoformat() + "Z"
    return value


def message_to_dict(doc: dict) -> dict:
    return {
        "id": oid_str(doc["_id"]),
        "thread_id": str(doc.get("thread_id") or ""),
        "sender_id": str(doc.get("sender_id") or ""),
        "sender_role": doc.get("sender_role") or "student",
        "sender_name": doc.get("sender_name") or "",
        "text": doc.get("text") or "",
        "created_at": _iso(doc.get("created_at")),
    }


def thread_to_dict(doc: dict) -> dict:
    return {
        "id": oid_str(doc["_id"]),
        "student_id": str(doc.get("student_id") or ""),
        "student_name": doc.get("student_name") or "",
        "student_email": doc.get("student_email") or "",
        "student_grade": doc.get("student_grade") or "",
        "last_message": doc.get("last_message") or "",
        "last_at": _iso(doc.get("last_at")),
        "unread_admin": int(doc.get("unread_admin") or 0),
        "unread_student": int(doc.get("unread_student") or 0),
        "created_at": _iso(doc.get("created_at")),
    }


def ensure_indexes():
    threads = col("chat_threads")
    messages = col("chat_messages")
    threads.create_index("student_id", unique=True)
    threads.create_index([("last_at", -1)])
    messages.create_index([("thread_id", 1), ("created_at", 1)])
    messages.create_index("created_at")


def get_or_create_student_thread(user: dict) -> dict:
    student_id = str(user["id"])
    existing = col("chat_threads").find_one({"student_id": student_id})
    if existing:
        # đồng bộ tên/lớp nếu đổi
        col("chat_threads").update_one(
            {"_id": existing["_id"]},
            {
                "$set": {
                    "student_name": user.get("full_name") or existing.get("student_name"),
                    "student_email": user.get("email") or existing.get("student_email"),
                    "student_grade": user.get("grade") or existing.get("student_grade") or "",
                }
            },
        )
        return col("chat_threads").find_one({"_id": existing["_id"]})

    now = datetime.utcnow()
    doc = {
        "student_id": student_id,
        "student_name": user.get("full_name") or "",
        "student_email": user.get("email") or "",
        "student_grade": user.get("grade") or "",
        "last_message": "",
        "last_at": now,
        "unread_admin": 0,
        "unread_student": 0,
        "created_at": now,
    }
    result = col("chat_threads").insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def list_admin_threads(limit: int = 100) -> list[dict]:
    cur = (
        col("chat_threads")
        .find({})
        .sort([("unread_admin", -1), ("last_at", -1)])
        .limit(max(1, min(limit, 200)))
    )
    return [thread_to_dict(d) for d in cur]


def get_thread(thread_id: str) -> dict | None:
    oid = parse_oid(thread_id)
    if not oid:
        return None
    return col("chat_threads").find_one({"_id": oid})


def list_messages(thread_id: str, *, after: str | None = None, before: str | None = None, limit: int = DEFAULT_LIMIT) -> list[dict]:
    tid = str(thread_id)
    query: dict[str, Any] = {"thread_id": tid}
    if after:
        try:
            after_dt = datetime.fromisoformat(after.replace("Z", ""))
            query["created_at"] = {"$gt": after_dt}
        except ValueError:
            pass
    elif before:
        try:
            before_dt = datetime.fromisoformat(before.replace("Z", ""))
            query["created_at"] = {"$lt": before_dt}
        except ValueError:
            pass

    cur = (
        col("chat_messages")
        .find(query)
        .sort("created_at", 1 if after else -1)
        .limit(max(1, min(int(limit or DEFAULT_LIMIT), 200)))
    )
    docs = list(cur)
    if not after:
        docs.reverse()
    return [message_to_dict(d) for d in docs]


def post_message(
    *,
    thread: dict,
    sender_id: str,
    sender_role: str,
    sender_name: str,
    text: str,
) -> dict:
    text = (text or "").strip()
    if not text:
        raise ValueError("Tin nhắn trống")
    if len(text) > MAX_TEXT:
        raise ValueError(f"Tin nhắn tối đa {MAX_TEXT} ký tự")

    now = datetime.utcnow()
    msg = {
        "thread_id": oid_str(thread["_id"]),
        "sender_id": str(sender_id),
        "sender_role": sender_role,
        "sender_name": sender_name or "",
        "text": text,
        "created_at": now,
    }
    result = col("chat_messages").insert_one(msg)
    msg["_id"] = result.inserted_id

    # Người gửi: xóa unread phía mình; phía kia +1
    if sender_role == "admin":
        set_fields = {
            "last_message": text[:200],
            "last_at": now,
            "unread_student": (thread.get("unread_student") or 0) + 1,
            "unread_admin": 0,
        }
    else:
        set_fields = {
            "last_message": text[:200],
            "last_at": now,
            "unread_admin": (thread.get("unread_admin") or 0) + 1,
            "unread_student": 0,
        }
    col("chat_threads").update_one({"_id": thread["_id"]}, {"$set": set_fields})

    return message_to_dict(msg)


def mark_read(*, thread: dict, reader_role: str) -> None:
    field = "unread_admin" if reader_role == "admin" else "unread_student"
    col("chat_threads").update_one({"_id": thread["_id"]}, {"$set": {field: 0}})


def poll_updates(*, role: str, user_id: str, since: datetime, thread_id: str | None = None) -> dict:
    """Lấy tin mới sau mốc since."""
    query: dict[str, Any] = {"created_at": {"$gt": since}}
    threads_out = []

    if role == "admin":
        if thread_id:
            query["thread_id"] = str(thread_id)
        msgs = list(col("chat_messages").find(query).sort("created_at", 1).limit(100))
        threads_out = list_admin_threads(80)
    else:
        thread = col("chat_threads").find_one({"student_id": str(user_id)})
        if not thread:
            return {"messages": [], "threads": [], "server_time": _iso(datetime.utcnow())}
        query["thread_id"] = oid_str(thread["_id"])
        msgs = list(col("chat_messages").find(query).sort("created_at", 1).limit(100))
        threads_out = [thread_to_dict(thread)]

    return {
        "messages": [message_to_dict(m) for m in msgs],
        "threads": threads_out,
        "server_time": _iso(datetime.utcnow()),
    }
