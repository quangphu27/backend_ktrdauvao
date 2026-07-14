from .auth import auth_bp
from .courses import courses_bp
from .questions import questions_bp
from .tests import tests_bp
from .admin import admin_bp
from .submissions import submissions_bp

__all__ = [
    "auth_bp",
    "courses_bp",
    "questions_bp",
    "tests_bp",
    "admin_bp",
    "submissions_bp",
]
