"""Seed: Kiểm tra Python bài 2 — 4 câu tự luận viết code."""

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions


QUESTIONS = [
    {
        "type": "python_code",
        "content": (
            "Câu 1: Viết chương trình nhập vào số nguyên n.\n"
            "Đếm xem từ 1 đến n có bao nhiêu số chia hết cho 3.\n\n"
            "Ví dụ:\n"
            "Nhập n: 20\n"
            "Kết quả:\n"
            "Có 6 số chia hết cho 3."
        ),
        "points": 2.5,
        "allow_run": True,
        "hint": "Dùng vòng for từ 1 đến n, nếu i % 3 == 0 thì đếm thêm 1.",
        "starter_code": "",
    },
    {
        "type": "python_code",
        "content": (
            "Câu 2: Viết chương trình nhập vào số nguyên n.\n"
            "Tìm số lớn nhất nhỏ hơn hoặc bằng n và chia hết cho 5.\n\n"
            "Ví dụ:\n"
            "Nhập n: 23\n"
            "Kết quả:\n"
            "20"
        ),
        "points": 2.5,
        "allow_run": True,
        "hint": "Có thể dùng n // 5 * 5, hoặc lùi dần từ n cho đến khi chia hết cho 5.",
        "starter_code": "",
    },
    {
        "type": "python_code",
        "content": (
            "Câu 3: Viết chương trình nhập vào 3 số nguyên a, b, c.\n"
            "Tìm và in ra số lớn nhất.\n\n"
            "Ví dụ:\n"
            "Nhập a: 15\n"
            "Nhập b: 8\n"
            "Nhập c: 20\n"
            "Kết quả:\n"
            "Số lớn nhất là 20"
        ),
        "points": 2.5,
        "allow_run": True,
        "hint": "Dùng if-elif hoặc hàm max(a, b, c).",
        "starter_code": "",
    },
    {
        "type": "python_code",
        "content": (
            "Câu 4: Viết chương trình nhập vào số nguyên n.\n"
            "Kiểm tra n có phải là số nguyên tố hay không.\n\n"
            "Ví dụ gợi ý:\n"
            "- n = 7 → là số nguyên tố\n"
            "- n = 9 → không phải số nguyên tố\n"
            "- n ≤ 1 → không phải số nguyên tố"
        ),
        "points": 2.5,
        "allow_run": True,
        "hint": (
            "Số nguyên tố > 1 và chỉ chia hết cho 1 và chính nó. "
            "Duyệt i từ 2 đến căn n (hoặc đến n-1), nếu n % i == 0 thì không phải."
        ),
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
            "title": "Kiểm tra Python bài 2",
            "description": (
                "Bài kiểm tra Python tự luận — 4 câu viết code "
                "(đếm chia hết cho 3, số chia hết cho 5, số lớn nhất, số nguyên tố). "
                "Em có thể bấm «Chạy thử» để kiểm tra chương trình."
            ),
            "slug": slug,
            "duration_minutes": 40,
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
        print(f"title={data['title']}")
        print(f"questions={len(data['questions'])}")
        print(f"public=/quiz/{data['slug']}")


if __name__ == "__main__":
    main()
