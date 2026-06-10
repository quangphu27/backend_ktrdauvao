"""Chạy seed thủ công: python seed_runner.py"""
import sys

from pymongo.errors import ServerSelectionTimeoutError

from app import create_app
from seed import seed_database

app = create_app()

try:
    with app.app_context():
        seed_database()
    print("Seed hoan tat!")
except ServerSelectionTimeoutError:
    print("LOI: Khong ket noi duoc MongoDB Atlas.")
    print("Chay 'python check_db.py' de xem huong dan chi tiet.")
    sys.exit(1)
