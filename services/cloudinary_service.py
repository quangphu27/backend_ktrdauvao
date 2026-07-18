"""Upload file lên Cloudinary."""

from __future__ import annotations

import re
from datetime import datetime

import cloudinary
import cloudinary.uploader
from flask import current_app


def _configure():
    url = current_app.config.get("CLOUDINARY_URL")
    if url:
        cloudinary.config(cloudinary_url=url)
        return
    cloudinary.config(
        cloud_name=current_app.config.get("CLOUDINARY_CLOUD_NAME"),
        api_key=current_app.config.get("CLOUDINARY_API_KEY"),
        api_secret=current_app.config.get("CLOUDINARY_API_SECRET"),
        secure=True,
    )


def _safe_folder_segment(value, fallback="hoc_sinh"):
    s = re.sub(r"[^\w\-]+", "_", (value or "").strip(), flags=re.UNICODE)
    return (s[:40] or fallback).strip("_") or fallback


def upload_submission_file(file_storage, student_name="", phone=""):
    """Upload 1 file (thường .sb3) lên Cloudinary, trả về metadata."""
    _configure()
    if not current_app.config.get("CLOUDINARY_API_KEY") and not current_app.config.get("CLOUDINARY_URL"):
        raise RuntimeError("Thiếu cấu hình Cloudinary trong .env")

    original = file_storage.filename or "file"
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    folder = (
        f"scratch3_submissions/"
        f"{_safe_folder_segment(student_name)}/"
        f"{_safe_folder_segment(phone, 'sdt')}"
    )
    public_id = f"{stamp}_{_safe_folder_segment(original.rsplit('.', 1)[0], 'bai')}"

    # .sb3/.zip => raw; ảnh => image; còn lại auto
    if ext in {"sb3", "sb2", "zip", "pdf", "doc", "docx", "txt"}:
        resource_type = "raw"
    elif ext in {"png", "jpg", "jpeg", "gif", "webp"}:
        resource_type = "image"
    else:
        resource_type = "auto"

    result = cloudinary.uploader.upload(
        file_storage,
        folder=folder,
        public_id=public_id,
        resource_type=resource_type,
        overwrite=False,
        use_filename=True,
        unique_filename=True,
    )
    return {
        "original_name": original,
        "url": result.get("secure_url") or result.get("url"),
        "public_id": result.get("public_id"),
        "resource_type": result.get("resource_type") or resource_type,
        "format": result.get("format") or ext,
        "bytes": result.get("bytes") or 0,
        "created_at": result.get("created_at"),
    }


def destroy_file(public_id, resource_type="raw"):
    if not public_id:
        return
    _configure()
    cloudinary.uploader.destroy(public_id, resource_type=resource_type)


def upload_image_file(file_storage, folder="quiz_images"):
    """Upload ảnh câu hỏi lên Cloudinary."""
    _configure()
    if not current_app.config.get("CLOUDINARY_API_KEY") and not current_app.config.get("CLOUDINARY_URL"):
        raise RuntimeError("Thiếu cấu hình Cloudinary trong .env")

    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    original = file_storage.filename or "image"
    base = _safe_folder_segment(original.rsplit(".", 1)[0], "img")
    result = cloudinary.uploader.upload(
        file_storage,
        folder=folder,
        public_id=f"{stamp}_{base}",
        resource_type="image",
        overwrite=False,
    )
    return {
        "url": result.get("secure_url") or result.get("url"),
        "public_id": result.get("public_id"),
    }

