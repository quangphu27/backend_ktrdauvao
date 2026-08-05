"""Seed: bài kiểm tra Python đầu tiên (5 câu tự luận)."""

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions


QUESTIONS = [
    {
        "type": "python_code",
        "content": "Câu 1: Nhập 2 số a, b. In ra màn hình tổng của 2 số đó.",
        "points": 2,
        "allow_run": True,
        "hint": "Dùng input() để nhập, int() để đổi sang số nguyên, print() để in tổng.",
        "starter_code": "",
    },
    {
        "type": "python_code",
        "content": (
            "Câu 2: Nhập vào 1 số nguyên n. Tính tổng S = 1 + 3 + 5 + ... + n\n"
            "(Nếu n chẵn thì cộng đến số lẻ gần nhất ≤ n)."
        ),
        "points": 2,
        "allow_run": True,
        "hint": "Dùng vòng for hoặc while, cộng các số lẻ từ 1 đến n.",
        "starter_code": "",
    },
    {
        "type": "python_code",
        "content": (
            "Câu 3: Viết chương trình in ra n số Fibonacci đầu tiên "
            "(1, 1, 2, 3, 5, 8, ...), với n được nhập vào từ bàn phím."
        ),
        "points": 2,
        "allow_run": True,
        "hint": "Fibonacci: số sau = tổng 2 số trước. Bắt đầu bằng 1, 1.",
        "starter_code": "",
    },
    {
        "type": "python_code",
        "content": (
            "Câu 4: Viết chương trình kiểm tra xem năm được nhập vào có phải năm nhuận không.\n"
            "(Năm nhuận: chia hết cho 400, hoặc chia hết cho 4 nhưng không chia hết cho 100)."
        ),
        "points": 2,
        "allow_run": True,
        "hint": "Năm nhuận nếu (năm % 400 == 0) hoặc (năm % 4 == 0 và năm % 100 != 0).",
        "starter_code": "",
    },
    {
        "type": "python_code",
        "content": (
            "Câu 5: Tạo 1 class TaiKhoan, có thuộc tính tendangnhap, matkhau, "
            "có phương thức DangNhap():\n"
            '- TH1: nếu tendangnhap = "admin" và matkhau = "admin" thì trả về True\n'
            "- TH2: các trường hợp còn lại trả về False\n\n"
            "Viết thêm phần kiểm thử: tạo đối tượng, gọi DangNhap() và in kết quả."
        ),
        "points": 2,
        "allow_run": True,
        "hint": "Dùng class, __init__, và phương thức DangNhap(self) trả về True/False.",
        "starter_code": "",
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
            "title": "Kiểm tra Python đầu tiên",
            "description": (
                "Bài kiểm tra Python tự luận — 5 câu viết code. "
                "Em có thể bấm «Chạy thử» để kiểm tra chương trình "
                "(điền dữ liệu nhập trước khi chạy)."
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
        print(f"public=/quiz/{data['slug']}")


if __name__ == "__main__":
    main()
