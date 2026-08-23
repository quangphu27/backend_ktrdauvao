"""Seed: Kiểm tra Python ngày 23-08 — 2 câu (xếp loại học sinh, ngày tiếp theo)."""

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
            "Câu 1 — Xếp loại học sinh\n\n"
            "Viết chương trình nhập điểm Toán, Văn, Anh (số thực).\n\n"
            "Yêu cầu:\n"
            "1. Tính điểm trung bình = (Toán + Văn + Anh) / 3\n"
            "2. Xếp loại theo điểm trung bình:\n"
            "   · ≥ 8     → Giỏi\n"
            "   · ≥ 6.5   → Khá\n"
            "   · ≥ 5     → Trung bình\n"
            "   · < 5     → Yếu\n\n"
            "Điều kiện thêm:\n"
            "Với học sinh Giỏi và Khá — không được có môn nào dưới 3 điểm.\n"
            "Nếu có môn < 3 thì hạ xuống Trung bình "
            "(hoặc Yếu nếu trung bình < 5).\n\n"
            "In ra điểm trung bình (1 chữ số thập phân) và xếp loại.\n\n"
            "Ví dụ 1:\n"
            "Toán: 8\n"
            "Văn: 9\n"
            "Anh: 8.5\n"
            "→ Trung bình: 8.5 — Xếp loại: Giỏi\n\n"
            "Ví dụ 2:\n"
            "Toán: 9\n"
            "Văn: 8\n"
            "Anh: 2\n"
            "→ Trung bình: 6.3 — Xếp loại: Trung bình "
            "(vì có môn dưới 3, không được Khá)"
        ),
        "points": 5,
        "allow_run": True,
        "hint": (
            "Tính tb = (toan + van + anh) / 3. "
            "Xếp loại theo tb, rồi kiểm tra: "
            "nếu loại Giỏi/Khá mà min(toan, van, anh) < 3 "
            "thì hạ xuống Trung bình (hoặc Yếu nếu tb < 5)."
        ),
        "starter_code": (
            "toan = float(input(\"Điểm Toán: \"))\n"
            "van = float(input(\"Điểm Văn: \"))\n"
            "anh = float(input(\"Điểm Anh: \"))\n\n"
            "# Tính trung bình và xếp loại tại đây\n"
        ),
    },
    {
        "type": "python_code",
        "content": (
            "Câu 2 — Ngày tiếp theo\n\n"
            "Viết chương trình nhập:\n"
            "· ngày (d)\n"
            "· tháng (m)\n"
            "· năm (y)\n\n"
            "In ra ngày tiếp theo theo dạng: dd/mm/yyyy\n\n"
            "Gợi ý số ngày trong tháng:\n"
            "· Tháng 1, 3, 5, 7, 8, 10, 12 → 31 ngày\n"
            "· Tháng 4, 6, 9, 11 → 30 ngày\n"
            "· Tháng 2 → 28 ngày (năm thường) hoặc 29 ngày (năm nhuận)\n\n"
            "Năm nhuận là gì?\n"
            "Năm nhuận là năm có 366 ngày (tháng 2 có 29 ngày).\n"
            "Quy tắc:\n"
            "· Năm chia hết cho 400 → nhuận\n"
            "· Hoặc năm chia hết cho 4 nhưng KHÔNG chia hết cho 100 → nhuận\n"
            "· Còn lại → không nhuận\n"
            "Ví dụ: 2000, 2024 là nhuận; 1900, 2023 không nhuận.\n\n"
            "Ví dụ:\n"
            "Nhập: 28 2 2024  →  29/02/2024\n"
            "Nhập: 29 2 2024  →  01/03/2024\n"
            "Nhập: 31 12 2023 →  01/01/2024\n"
            "Nhập: 15 8 2025  →  16/08/2025"
        ),
        "points": 5,
        "allow_run": True,
        "hint": (
            "Viết hàm so_ngay(thang, nam). "
            "Năm nhuận: (y % 400 == 0) or (y % 4 == 0 and y % 100 != 0). "
            "Nếu ngày < số ngày tháng → ngày += 1; "
            "ngược lại ngày = 1, tháng += 1; "
            "nếu tháng > 12 → tháng = 1, năm += 1."
        ),
        "starter_code": (
            "d = int(input(\"Ngày: \"))\n"
            "m = int(input(\"Tháng: \"))\n"
            "y = int(input(\"Năm: \"))\n\n"
            "def la_nam_nhuan(nam):\n"
            "    return (nam % 400 == 0) or (nam % 4 == 0 and nam % 100 != 0)\n\n"
            "def so_ngay_trong_thang(thang, nam):\n"
            "    # TODO: trả về số ngày của tháng\n"
            "    pass\n\n"
            "# Tính ngày tiếp theo và in ra dạng dd/mm/yyyy\n"
        ),
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
            "title": "Kiểm tra Python ngày 23-08",
            "description": (
                "Bài kiểm tra Python tự luận — 2 câu viết code "
                "(xếp loại học sinh theo điểm TB, tính ngày tiếp theo / năm nhuận). "
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
        print(f"questions={len(data['questions'])}")
        print(f"public=/quiz/{data['slug']}")


if __name__ == "__main__":
    main()
