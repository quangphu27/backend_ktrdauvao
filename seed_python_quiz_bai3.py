"""Seed: Kiểm tra Python bài 3 — 4 câu (giai thừa, list, class, file)."""

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions


TAIKHOAN_TXT = """admin
hocsinh01
nguyenvana
tranthib
phamvana
teacher
codekids
"""

QUESTIONS = [
    {
        "type": "python_code",
        "content": (
            "Câu 1: Nhập vào số tự nhiên n và đưa ra màn hình n!.\n"
            "Biết n! = 1 × 2 × 3 × 4 × … × n\n\n"
            "Ví dụ: 5! = 1 × 2 × 3 × 4 × 5 = 120"
        ),
        "points": 2.5,
        "allow_run": True,
        "hint": "Dùng vòng for từ 1 đến n, nhân dồn vào biến kết quả (bắt đầu = 1).",
        "starter_code": "",
    },
    {
        "type": "python_code",
        "content": (
            "Câu 2: Cho danh sách:\n"
            "danhsach = [1, 6, 4, 2, 510, 19]\n\n"
            "Viết chương trình tìm số lớn nhất, số nhỏ nhất, "
            "và giá trị trung bình của danh sách."
        ),
        "points": 2.5,
        "allow_run": True,
        "hint": "Có thể dùng max(), min(), sum()/len() hoặc tự viết vòng lặp.",
        "starter_code": "danhsach = [1, 6, 4, 2, 510, 19]\n\n",
    },
    {
        "type": "python_code",
        "content": (
            "Câu 3: Tạo 1 lớp HinhTron có thuộc tính bán kính, "
            "có phương thức tính chu vi và diện tích của hình tròn.\n\n"
            "Gợi ý công thức:\n"
            "- Chu vi = 2 × π × r\n"
            "- Diện tích = π × r²\n"
            "(Có thể lấy π ≈ 3.14 hoặc import math)"
        ),
        "points": 2.5,
        "allow_run": True,
        "hint": "Dùng class, __init__(self, ban_kinh), và 2 phương thức (vd: chu_vi, dien_tich). Tạo đối tượng để kiểm thử.",
        "starter_code": "",
    },
    {
        "type": "python_code",
        "content": (
            "Câu 4: Nhập vào 1 username (chuỗi ký tự), "
            "kiểm tra xem username có tồn tại trong file taikhoan.txt hay không.\n\n"
            "File taikhoan.txt đã có sẵn bên trái — mỗi dòng là một username.\n"
            "In ra thông báo phù hợp (vd: «Tồn tại» / «Không tồn tại»)."
        ),
        "points": 2.5,
        "allow_run": True,
        "hint": (
            "Dùng open(\"taikhoan.txt\", \"r\"), đọc các dòng, "
            "so sánh với username đã nhập (nhớ strip() khoảng trắng/xuống dòng)."
        ),
        "starter_code": "",
        "sample_files": [
            {
                "name": "taikhoan.txt",
                "content": TAIKHOAN_TXT,
            }
        ],
    },
]


def main():
    app = create_app()
    with app.app_context():
        questions = sanitize_questions(QUESTIONS)
        slug = None
        for _ in range(20):
            candidate = generate_quiz_slug()
            if not col("quizzes").find_one({"slug": candidate}):
                slug = candidate
                break
        if not slug:
            raise RuntimeError("Không tạo được slug")

        now = datetime.utcnow()
        doc = {
            "title": "Kiểm tra Python bài 3",
            "description": (
                "Bài kiểm tra Python tự luận — 4 câu viết code "
                "(giai thừa, list, class HinhTron, đọc file taikhoan.txt). "
                "Em có thể bấm «Chạy thử» để kiểm tra chương trình."
            ),
            "slug": slug,
            "duration_minutes": 45,
            "is_active": True,
            "questions": questions,
            "created_at": now,
            "updated_at": now,
        }
        result = col("quizzes").insert_one(doc)
        doc["_id"] = result.inserted_id
        data = quiz_to_dict(doc, include_answers=True)
        print("CREATED")
        print(f"id={data['id']}")
        print(f"slug={data['slug']}")
        print(f"questions={len(data['questions'])}")
        print(f"public=/quiz/{data['slug']}")


if __name__ == "__main__":
    main()
