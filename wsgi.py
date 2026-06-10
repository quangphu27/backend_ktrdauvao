import sys
import os

PROJECT_HOME = os.path.dirname(os.path.abspath(__file__))
if PROJECT_HOME not in sys.path:
    sys.path.insert(0, PROJECT_HOME)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_HOME, ".env"))

from app import create_app

application = create_app()

# Không seed khi khởi động WSGI (tránh treo web app nếu MongoDB chậm/lỗi).
# Chạy seed thủ công trên PythonAnywhere Bash console:
#   cd ~/path/to/backend && python seed_runner.py
