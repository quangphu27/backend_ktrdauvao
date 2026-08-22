"""Seed: Kiểm tra Python ngày 16-08 — 4 câu (phân số, hỗn số, nguyên tố, UCLN/BCNN)."""

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
            "Câu 1: Viết chương trình cộng 2 phân số a/b + c/d.\n"
            "Kết quả là 1 phân số đã được rút gọn.\n\n"
            "Ví dụ:\n"
            "1/4 + 1/4 = 1/2"
        ),
        "points": 2.5,
        "allow_run": True,
        "hint": (
            "Quy đồng mẫu số, cộng tử số, rồi rút gọn bằng UCLN "
            "(math.gcd hoặc tự viết hàm gcd)."
        ),
        "starter_code": "",
    },
    {
        "type": "python_code",
        "content": (
            "Câu 2: Viết chương trình kiểm tra 1 phân số lớn hơn, bằng 1 hay nhỏ hơn 1.\n"
            "Nếu phân số lớn hơn 1 thì viết thành hỗn số.\n\n"
            "Ví dụ:\n"
            "Phân số 5/3 lớn hơn 1 → viết lại thành 1 (2/3)"
        ),
        "points": 2.5,
        "allow_run": True,
        "hint": (
            "So sánh tử và mẫu. Nếu tử > mẫu: phần nguyên = tử // mẫu, "
            "phân số phần = tử % mẫu / mẫu (rút gọn phần phân số)."
        ),
        "starter_code": "",
    },
    {
        "type": "python_code",
        "content": (
            "Câu 3: Viết chương trình nhập vào số nguyên n.\n"
            "Kiểm tra n là số nguyên tố hay hợp số, "
            "và có phải là số may mắn hay không.\n\n"
            "Ví dụ:\n"
            "- Số 18 là hợp số, số 18 là số may mắn\n"
            "- Số 5 là số nguyên tố\n"
            "- Số 7 là số nguyên tố, số 7 không phải là số may mắn\n\n"
            "Gợi ý: Số may mắn là số có chứa chữ số 8."
        ),
        "points": 2.5,
        "allow_run": True,
        "hint": (
            "Nguyên tố: n > 1 và không có ước từ 2 đến n-1. "
            "Số may mắn (theo đề): có chữ số '8' trong n."
        ),
        "starter_code": "",
    },
    {
        "type": "python_code",
        "content": (
            "Câu 4: Viết chương trình nhập vào 2 số a, b.\n"
            "Tìm UCLN và BCNN của 2 số đó.\n\n"
            "Gợi ý:\n"
            "- UCLN: ước chung lớn nhất\n"
            "- BCNN = |a × b| / UCLN"
        ),
        "points": 2.5,
        "allow_run": True,
        "hint": "Có thể dùng thuật toán Euclid cho UCLN, rồi tính BCNN.",
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
            "title": "Kiểm tra Python ngày 16-08",
            "description": (
                "Bài kiểm tra Python tự luận — 4 câu viết code "
                "(cộng phân số, hỗn số, nguyên tố/số may mắn, UCLN/BCNN). "
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
