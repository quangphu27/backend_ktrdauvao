"""Quản lý báo cáo Excel: local khi dev, frontend tĩnh + MongoDB khi deploy."""

from __future__ import annotations

import json
import os
import time
from datetime import datetime
from io import BytesIO
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

from bson.binary import Binary
from flask import Blueprint, current_app, jsonify, request, send_file
from flask_jwt_extended import get_jwt, jwt_required
from openpyxl import load_workbook

from database import col


reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

ALLOWED_EXTENSIONS = {".xlsx", ".xlsm"}
MAX_ROWS = 2000
MAX_COLUMNS = 200
MAX_STORED_BYTES = 15 * 1024 * 1024
REMOTE_CACHE_SECONDS = 300
_remote_cache = {"at": 0.0, "files": []}


def _admin_required():
    return get_jwt().get("role") == "admin"


def _reports_root() -> Path:
    configured = os.getenv("TEACHING_REPORTS_FOLDER")
    if configured:
        return Path(configured).resolve()
    return (Path(current_app.root_path).parent / "frontend" / "public" / "Baocaodayhoc").resolve()


def _normalize_path(relative_path: str) -> str:
    value = (relative_path or "").replace("\\", "/").strip("/")
    if not value or value.startswith("../") or "/../" in value:
        raise ValueError("Đường dẫn file không hợp lệ")
    if Path(value).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("Chỉ hỗ trợ file .xlsx và .xlsm")
    return value


def _safe_local_file(relative_path: str) -> Path:
    value = _normalize_path(relative_path)
    root = _reports_root()
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("Đường dẫn file không hợp lệ") from exc
    return candidate


def _fetch_json(url: str):
    req = Request(url, headers={"User-Agent": "kiemtradauvao-reports"})
    with urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def _remote_report_files():
    now = time.time()
    if now - _remote_cache["at"] < REMOTE_CACHE_SECONDS:
        return _remote_cache["files"]

    frontend_url = (
        current_app.config.get("FRONTEND_URL")
        or os.getenv("FRONTEND_URL")
        or "https://kiemtradauvao.vercel.app"
    ).rstrip("/")
    url = f"{frontend_url}/Baocaodayhoc/manifest.json"
    payload = _fetch_json(url)
    files = []
    for item in payload.get("files") or []:
        relative = _normalize_path(item.get("path") or "")
        if Path(relative).suffix.lower() not in ALLOWED_EXTENSIONS:
            continue
        parts = relative.split("/")
        files.append({
            "name": parts[-1],
            "path": relative,
            "size": int(item.get("size") or 0),
            "updated_at": None,
            "source": "github",
        })
    _remote_cache.update({"at": now, "files": files})
    return files


def _remote_file_bytes(relative_path: str) -> bytes:
    frontend_url = (
        current_app.config.get("FRONTEND_URL")
        or os.getenv("FRONTEND_URL")
        or "https://kiemtradauvao.vercel.app"
    ).rstrip("/")
    url = f"{frontend_url}/Baocaodayhoc/{quote(relative_path, safe='/')}"
    req = Request(url, headers={"User-Agent": "kiemtradauvao-reports"})
    with urlopen(req, timeout=30) as response:
        return response.read()


def _saved_reports():
    docs = col("teaching_reports").find(
        {},
        {"path": 1, "name": 1, "size": 1, "updated_at": 1},
    )
    result = []
    for doc in docs:
        updated = doc.get("updated_at")
        result.append({
            "name": doc.get("name") or Path(doc["path"]).name,
            "path": doc["path"],
            "size": int(doc.get("size") or 0),
            "updated_at": updated.timestamp() if isinstance(updated, datetime) else updated,
            "source": "database",
        })
    return result


def _all_report_files():
    # Website frontend cung cấp file gốc; local và DB ghi đè theo cùng path.
    by_path = {}
    try:
        for item in _remote_report_files():
            by_path[item["path"]] = item
    except Exception as exc:
        current_app.logger.warning("Không đọc được danh sách báo cáo từ frontend: %s", exc)

    root = _reports_root()
    if root.is_dir():
        for path in sorted(root.rglob("*"), key=lambda p: str(p).lower()):
            if not path.is_file() or path.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue
            relative = path.relative_to(root).as_posix()
            stat = path.stat()
            by_path[relative] = {
                "name": path.name,
                "path": relative,
                "size": stat.st_size,
                "updated_at": stat.st_mtime,
                "source": "local",
            }

    for item in _saved_reports():
        by_path[item["path"]] = item
    return sorted(by_path.values(), key=lambda item: item["path"].lower())


def _report_bytes(relative_path: str):
    value = _normalize_path(relative_path)
    saved = col("teaching_reports").find_one({"path": value})
    if saved and saved.get("content") is not None:
        return bytes(saved["content"]), "database"

    local = _safe_local_file(value)
    if local.is_file():
        return local.read_bytes(), "local"

    known_paths = {item["path"] for item in _remote_report_files()}
    if value not in known_paths:
        raise FileNotFoundError(value)
    return _remote_file_bytes(value), "github"


def _store_report(relative_path: str, content: bytes, source: str):
    if len(content) > MAX_STORED_BYTES:
        raise ValueError("File sau khi lưu vượt quá giới hạn 15 MB")

    if source == "local":
        path = _safe_local_file(relative_path)
        path.write_bytes(content)
        return

    col("teaching_reports").update_one(
        {"path": relative_path},
        {
            "$set": {
                "path": relative_path,
                "name": Path(relative_path).name,
                "content": Binary(content),
                "size": len(content),
                "updated_at": datetime.utcnow(),
            }
        },
        upsert=True,
    )


def _cell_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


@reports_bp.route("", methods=["GET"])
@jwt_required()
def list_reports():
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403

    try:
        files = _all_report_files()
    except Exception as exc:
        current_app.logger.exception("Không tải được danh sách báo cáo")
        return jsonify({"message": f"Không tải được danh sách báo cáo: {exc}"}), 500

    grouped = {}
    for item in files:
        parts = item["path"].split("/")
        class_name = parts[0] if len(parts) > 1 else "Chưa phân lớp"
        grouped.setdefault(class_name, []).append(item)

    classes = [
        {"name": name, "files": class_files}
        for name, class_files in sorted(grouped.items(), key=lambda item: item[0].lower())
    ]
    return jsonify({"classes": classes, "file_count": len(files)})


@reports_bp.route("/file", methods=["GET"])
@jwt_required()
def read_report():
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403

    try:
        relative_path = _normalize_path(request.args.get("path"))
        content, _source = _report_bytes(relative_path)
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 400
    except FileNotFoundError:
        return jsonify({"message": "Không tìm thấy file báo cáo"}), 404
    except Exception as exc:
        current_app.logger.exception("Không tải được file báo cáo")
        return jsonify({"message": f"Không tải được file báo cáo: {exc}"}), 502

    try:
        workbook = load_workbook(
            BytesIO(content),
            data_only=False,
            keep_vba=Path(relative_path).suffix.lower() == ".xlsm",
        )
        sheets = []
        for sheet in workbook.worksheets:
            row_count = min(sheet.max_row or 1, MAX_ROWS)
            column_count = min(sheet.max_column or 1, MAX_COLUMNS)
            rows = [
                [
                    _cell_value(sheet.cell(row=row, column=column).value)
                    for column in range(1, column_count + 1)
                ]
                for row in range(1, row_count + 1)
            ]
            sheets.append({
                "name": sheet.title,
                "rows": rows,
                "row_count": row_count,
                "column_count": column_count,
                "truncated": (
                    (sheet.max_row or 1) > MAX_ROWS
                    or (sheet.max_column or 1) > MAX_COLUMNS
                ),
            })
        workbook.close()
        return jsonify({
            "name": Path(relative_path).name,
            "path": relative_path,
            "sheets": sheets,
        })
    except Exception as exc:
        current_app.logger.exception("Không đọc được Excel %s", relative_path)
        return jsonify({"message": f"Không đọc được file Excel: {exc}"}), 400


@reports_bp.route("/file", methods=["PUT"])
@jwt_required()
def update_report():
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403

    data = request.get_json(silent=True) or {}
    try:
        relative_path = _normalize_path(data.get("path"))
        content, source = _report_bytes(relative_path)
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 400
    except FileNotFoundError:
        return jsonify({"message": "Không tìm thấy file báo cáo"}), 404
    except Exception as exc:
        return jsonify({"message": f"Không tải được file để chỉnh sửa: {exc}"}), 502

    changes = data.get("changes") or []
    if not isinstance(changes, list) or len(changes) > 10000:
        return jsonify({"message": "Danh sách thay đổi không hợp lệ hoặc quá lớn"}), 400

    try:
        workbook = load_workbook(
            BytesIO(content),
            data_only=False,
            keep_vba=Path(relative_path).suffix.lower() == ".xlsm",
        )
        changed = 0
        for item in changes:
            if not isinstance(item, dict):
                continue
            sheet_name = str(item.get("sheet") or "")
            row = int(item.get("row") or 0)
            column = int(item.get("column") or 0)
            if sheet_name not in workbook.sheetnames:
                continue
            if not (1 <= row <= MAX_ROWS and 1 <= column <= MAX_COLUMNS):
                continue
            workbook[sheet_name].cell(row=row, column=column).value = item.get("value")
            changed += 1

        output = BytesIO()
        workbook.save(output)
        workbook.close()
        _store_report(relative_path, output.getvalue(), source)
        return jsonify({"message": "Đã lưu báo cáo", "changed": changed})
    except Exception as exc:
        current_app.logger.exception("Không lưu được Excel %s", relative_path)
        return jsonify({"message": f"Không lưu được file Excel: {exc}"}), 400


@reports_bp.route("/download", methods=["GET"])
@jwt_required()
def download_report():
    if not _admin_required():
        return jsonify({"message": "Không có quyền truy cập"}), 403

    try:
        relative_path = _normalize_path(request.args.get("path"))
        content, _source = _report_bytes(relative_path)
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 400
    except FileNotFoundError:
        return jsonify({"message": "Không tìm thấy file báo cáo"}), 404
    except Exception as exc:
        return jsonify({"message": f"Không tải được file báo cáo: {exc}"}), 502

    return send_file(
        BytesIO(content),
        as_attachment=True,
        download_name=Path(relative_path).name,
    )
