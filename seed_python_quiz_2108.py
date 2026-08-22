"""Seed: Kiểm tra Python ngày 21-08 — 3 câu (tiền mua hàng, chia 3/5, ước số)."""

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
            "Câu 1 – Tính tiền mua hàng\n\n"
            "Một cửa hàng bán vở với giá 8.000 đồng/quyển và bút với giá 5.000 đồng/cây.\n\n"
            "Viết chương trình cho phép nhập:\n"
            "- Số quyển vở cần mua\n"
            "- Số cây bút cần mua\n\n"
            "Tính tổng số tiền phải trả.\n"
            "Nếu tổng tiền từ 100.000 đồng trở lên, khách hàng được giảm 10%. "
            "Hãy in ra số tiền cuối cùng phải trả.\n\n"
            "Ví dụ:\n"
            "Số vở: 10\n"
            "Số bút: 6\n\n"
            "Tổng tiền: 110000 đồng\n"
            "Giảm giá: 11000 đồng\n"
            "Số tiền phải trả: 99000 đồng"
        ),
        "points": 3,
        "allow_run": True,
        "hint": (
            "Tổng = vở × 8000 + bút × 5000. "
            "Nếu tổng >= 100000 thì giảm 10%, in tổng / giảm / số tiền cuối."
        ),
        "starter_code": "",
    },
    {
        "type": "python_code",
        "content": (
            "Câu 2: Nhập vào số nguyên dương n. Hãy viết chương trình:\n\n"
            "- Tìm tất cả các số từ 1 đến n chia hết cho 3 hoặc 5\n"
            "- Tính tổng các số đó\n"
            "- Đếm xem có bao nhiêu số\n"
            "- In ra số lớn nhất trong các số tìm được"
        ),
        "points": 3,
        "allow_run": True,
        "hint": (
            "Dùng vòng for từ 1 đến n, điều kiện i % 3 == 0 or i % 5 == 0. "
            "Lưu vào list hoặc cộng dồn / đếm / max."
        ),
        "starter_code": "",
    },
    {
        "type": "python_code",
        "content": (
            "Câu 3: Nhập vào số nguyên dương n. Viết chương trình thực hiện:\n\n"
            "- In ra tất cả ước số của n\n"
            "- Đếm số lượng ước của n\n"
            "- Tính tổng các ước của n\n"
            "- Kiểm tra n có phải là số hoàn hảo hay không\n\n"
            "Gợi ý: Số hoàn hảo là số bằng tổng các ước của nó (không tính chính n). "
            "Ví dụ: 6 = 1 + 2 + 3."
        ),
        "points": 4,
        "allow_run": True,
        "hint": (
            "Duyệt i từ 1 đến n, nếu n % i == 0 thì i là ước. "
            "Số hoàn hảo: tổng ước (trừ n) == n."
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
            "title": "Kiểm tra Python ngày 21-08",
            "description": (
                "Bài kiểm tra Python tự luận — 3 câu viết code "
                "(tính tiền mua hàng, số chia hết cho 3 hoặc 5, ước số & số hoàn hảo). "
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
