from .auth import auth_bp
from .courses import courses_bp
from .questions import questions_bp
from .tests import tests_bp
from .admin import admin_bp
from .submissions import submissions_bp
from .quizzes import quizzes_bp
from .classrooms import classrooms_bp
from .games import games_bp
from .reports import reports_bp
from .live import live_bp
from .scratch_labs import scratch_labs_bp
from .scratch_arena_api import scratch_arena_bp
from .iq300 import iq300_bp
from .chat import chat_bp

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
    "reports_bp",
    "live_bp",
    "scratch_labs_bp",
    "scratch_arena_bp",
    "iq300_bp",
    "chat_bp",
]
