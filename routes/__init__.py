from .auth import auth_bp
from .courses import courses_bp
from .questions import questions_bp
from .tests import tests_bp
from .admin import admin_bp
from .submissions import submissions_bp
from .quizzes import quizzes_bp
from .classrooms import classrooms_bp
from .games import games_bp

__all__ = [
    "auth_bp",
    "courses_bp",
    "questions_bp",
    "tests_bp",
    "admin_bp",
    "submissions_bp",
    "quizzes_bp",
    "classrooms_bp",
    "games_bp",
]
