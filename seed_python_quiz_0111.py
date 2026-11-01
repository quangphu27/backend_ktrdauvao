"""Seed: Bài kiểm tra Python đầu tháng 11 — 5 tự luận (math)."""

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions

QUIZ_TITLE = "Bài kiểm tra Python đầu tháng 11"
FIXED_SLUG = "python-0111"


def build_questions():
    questions = []

    questions.append({
        "type": "python_code",
        "content": (
            "Câu 1 — ĐƯỜNG CHÉO HÌNH CHỮ NHẬT\n\n"
            "Nhập chiều dài a và chiều rộng b của một hình chữ nhật. "
            "Tính độ dài đường chéo của hình chữ nhật.\n\n"
            "Công thức:\n"
            "d = √(a² + b²)"
        ),
        "points": 20,
        "allow_run": True,
        "function_name": "duong_cheo",
        "hint": "",
        "starter_code": "import math\n\n",
        "testcases": [
            {"name": "3-4-5", "mode": "function", "function_name": "duong_cheo", "args": [3, 4], "expected": 5},
            {"name": "5-12-13", "mode": "function", "function_name": "duong_cheo", "args": [5, 12], "expected": 13},
            {"name": "6-8-10", "mode": "function", "function_name": "duong_cheo", "args": [6, 8], "expected": 10},
            {"name": "0-0", "mode": "function", "function_name": "duong_cheo", "args": [0, 0], "expected": 0},
            {"name": "9-12-15", "mode": "function", "function_name": "duong_cheo", "args": [9, 12], "expected": 15},
        ],
        "order_num": 0,
    })

    questions.append({
        "type": "python_code",
        "content": (
            "Câu 2 — KHOẢNG CÁCH HAI THÀNH PHỐ\n\n"
            "Trên một bản đồ tọa độ, hai thành phố A và B có tọa độ lần lượt là "
            "A(x₁, y₁) và B(x₂, y₂).\n\n"
            "Nhập tọa độ của hai thành phố. Tính khoảng cách giữa chúng.\n\n"
            "Công thức:\n"
            "d = √((x₂ − x₁)² + (y₂ − y₁)²)"
        ),
        "points": 20,
        "allow_run": True,
        "function_name": "khoang_cach",
        "hint": "",
        "starter_code": "import math\n\n",
        "testcases": [
            {"name": "O→(3,4)", "mode": "function", "function_name": "khoang_cach", "args": [0, 0, 3, 4], "expected": 5},
            {"name": "(1,1)→(4,5)", "mode": "function", "function_name": "khoang_cach", "args": [1, 1, 4, 5], "expected": 5},
            {"name": "Trùng nhau", "mode": "function", "function_name": "khoang_cach", "args": [2, 3, 2, 3], "expected": 0},
            {"name": "(0,0)→(5,12)", "mode": "function", "function_name": "khoang_cach", "args": [0, 0, 5, 12], "expected": 13},
            {"name": "(-1,-1)→(2,3)", "mode": "function", "function_name": "khoang_cach", "args": [-1, -1, 2, 3], "expected": 5},
        ],
        "order_num": 1,
    })

    questions.append({
        "type": "python_code",
        "content": (
            "Câu 3 — SỐ CHÍNH PHƯƠNG\n\n"
            "Một số nguyên dương được gọi là số chính phương nếu nó bằng bình phương của một số nguyên.\n\n"
            "Nhập số nguyên dương n. Kiểm tra và thông báo n có phải số chính phương hay không.\n\n"
            "n là số chính phương nếu tồn tại số nguyên k sao cho n = k²."
        ),
        "points": 20,
        "allow_run": True,
        "function_name": "la_chinh_phuong",
        "hint": "",
        "starter_code": "import math\n\n",
        "testcases": [
            {"name": "16 đúng", "mode": "function", "function_name": "la_chinh_phuong", "args": [16], "expected": True},
            {"name": "15 sai", "mode": "function", "function_name": "la_chinh_phuong", "args": [15], "expected": False},
            {"name": "1 đúng", "mode": "function", "function_name": "la_chinh_phuong", "args": [1], "expected": True},
            {"name": "100 đúng", "mode": "function", "function_name": "la_chinh_phuong", "args": [100], "expected": True},
            {"name": "2 sai", "mode": "function", "function_name": "la_chinh_phuong", "args": [2], "expected": False},
            {"name": "81 đúng", "mode": "function", "function_name": "la_chinh_phuong", "args": [81], "expected": True},
        ],
        "order_num": 2,
    })

    questions.append({
        "type": "python_code",
        "content": (
            "Câu 4 — TỔNG GIAI THỪA\n\n"
            "Nhập số nguyên dương n. Tính tổng:\n"
            "S = 1! + 2! + 3! + ⋯ + n!"
        ),
        "points": 20,
        "allow_run": True,
        "function_name": "tong_giai_thua",
        "hint": "",
        "starter_code": "import math\n\n",
        "testcases": [
            {"name": "n=1", "mode": "function", "function_name": "tong_giai_thua", "args": [1], "expected": 1},
            {"name": "n=3", "mode": "function", "function_name": "tong_giai_thua", "args": [3], "expected": 9},
            {"name": "n=4", "mode": "function", "function_name": "tong_giai_thua", "args": [4], "expected": 33},
            {"name": "n=5", "mode": "function", "function_name": "tong_giai_thua", "args": [5], "expected": 153},
            {"name": "n=6", "mode": "function", "function_name": "tong_giai_thua", "args": [6], "expected": 873},
        ],
        "order_num": 3,
    })

    questions.append({
        "type": "python_code",
        "content": (
            "Câu 5 — BIỂU THỨC KẾT HỢP (CỘNG, TRỪ, PHÂN SỐ)\n\n"
            "Cho số thực x và số nguyên không âm n. Tính:\n"
            "K = (√|x| + n!) / (|x|ⁿ + 1) − n! / (n + 1)"
        ),
        "points": 20,
        "allow_run": True,
        "function_name": "ket_hop",
        "hint": "",
        "starter_code": "import math\n\n",
        "testcases": [
            {"name": "x=4 n=1 → 0.1", "mode": "function", "function_name": "ket_hop", "args": [4, 1], "expected": 0.1},
            {"name": "x=-9 n=1 → -0.1", "mode": "function", "function_name": "ket_hop", "args": [-9, 1], "expected": -0.1},
            {"name": "x=16 n=0 → 1.5", "mode": "function", "function_name": "ket_hop", "args": [16, 0], "expected": 1.5},
            {"name": "x=0 n=3 → 4.5", "mode": "function", "function_name": "ket_hop", "args": [0, 3], "expected": 4.5},
            {"name": "x=4 n=2", "mode": "function", "function_name": "ket_hop", "args": [4, 2], "expected": -22 / 51},
            {"name": "x=9 n=2", "mode": "function", "function_name": "ket_hop", "args": [9, 2], "expected": 5 / 82 - 2 / 3},
        ],
        "order_num": 4,
    })

    return questions


def main():
    app = create_app()
    with app.app_context():
        questions = sanitize_questions(build_questions())
        description = (
            "Bài kiểm tra Python đầu tháng 11 — 5 câu tự luận (module math): "
            "Đường chéo HCN · Khoảng cách 2 điểm · Số chính phương · Tổng giai thừa · "
            "Biểu thức kết hợp (cộng, trừ, phân số — sqrt, pow, fabs, factorial). Chấm bằng testcase (hàm)."
        )
        now = datetime.utcnow()
        existing = col("quizzes").find_one({"title": QUIZ_TITLE}) or col("quizzes").find_one(
            {"slug": FIXED_SLUG}
        )

        if existing:
            col("quizzes").update_one(
                {"_id": existing["_id"]},
                {
                    "$set": {
                        "title": QUIZ_TITLE,
                        "questions": questions,
                        "description": description,
                        "slug": FIXED_SLUG,
                        "duration_minutes": 45,
                        "is_active": True,
                        "updated_at": now,
                    }
                },
            )
            existing.update({
                "title": QUIZ_TITLE,
                "questions": questions,
                "slug": FIXED_SLUG,
                "description": description,
            })
            data = quiz_to_dict(existing, include_answers=True)
            print("UPDATED")
        else:
            slug = FIXED_SLUG
            if col("quizzes").find_one({"slug": FIXED_SLUG}):
                slug = None
                for _ in range(20):
                    candidate = generate_quiz_slug()
                    if not col("quizzes").find_one({"slug": candidate}):
                        slug = candidate
                        break
                if not slug:
                    raise RuntimeError("Không tạo được slug")

            doc = {
                "title": QUIZ_TITLE,
                "description": description,
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
        mc = sum(1 for q in data["questions"] if q.get("type") == "mcq")
        tl = sum(1 for q in data["questions"] if q.get("type") == "python_code")
        pts = sum(int(q.get("points") or 0) for q in data["questions"])
        print(f"mcq={mc} code={tl} total_points={pts}")
        print(f"public=/quiz/{data['slug']}")


if __name__ == "__main__":
    main()
