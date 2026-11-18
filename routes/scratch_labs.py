"""API bài lab Scratch làm trên web + chấm khối."""

from flask import Blueprint, jsonify, request

from data.scratch_labs_catalog import LABS, get_lab, public_lab
from services.scratch_grade_service import grade_project

scratch_labs_bp = Blueprint("scratch_labs", __name__, url_prefix="/api/scratch-labs")


@scratch_labs_bp.get("")
def list_labs():
    items = [public_lab(lab) for lab in sorted(LABS, key=lambda x: x.get("order", 0))]
    return jsonify({"labs": items})


@scratch_labs_bp.get("/<slug>")
def lab_detail(slug):
    lab = get_lab(slug)
    if not lab:
        return jsonify({"error": "Không tìm thấy bài"}), 404
    return jsonify({"lab": public_lab(lab)})


@scratch_labs_bp.post("/<slug>/grade")
def grade_lab(slug):
    lab = get_lab(slug)
    if not lab:
        return jsonify({"error": "Không tìm thấy bài"}), 404
    body = request.get_json(silent=True) or {}
    project = body.get("project")
    if project is None:
        return jsonify({"error": "Thiếu project"}), 400
    result = grade_project(project, lab.get("solution"))
    return jsonify(result)
