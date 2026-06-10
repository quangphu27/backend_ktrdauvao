from flask import Blueprint, jsonify
from database import col
from models import course_to_dict

courses_bp = Blueprint("courses", __name__, url_prefix="/api/courses")


@courses_bp.route("", methods=["GET"])
def get_courses():
    courses = col("courses").find().sort("name", 1)
    return jsonify([course_to_dict(c) for c in courses])
