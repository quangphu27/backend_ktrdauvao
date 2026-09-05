"""Seed: Kiểm tra Python — 20 trắc nghiệm lý thuyết + 2 tự luận code (có testcase)."""

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions

QUIZ_TITLE = "Kiểm tra Python — 20 TN + tự luận"
FIXED_SLUG = "python-20-tn-tl"


def mcq(num, content, options, correct_idx, explanation):
    opts = [{"text": t, "is_correct": i == correct_idx} for i, t in enumerate(options)]
    return {
        "type": "mcq",
        "content": f"Câu {num}: {content}",
        "points": 1,
        "options": opts,
        "explanation": explanation.strip(),
        "order_num": num - 1,
    }


RAW = [
    mcq(
        1,
        "Python là loại ngôn ngữ lập trình nào?",
        ["Ngôn ngữ máy", "Ngôn ngữ thông dịch", "Ngôn ngữ biên dịch", "Ngôn ngữ truy vấn"],
        1,
        """A. Ngôn ngữ máy – Sai.
B. Ngôn ngữ thông dịch – Đúng: Python chạy qua trình thông dịch.
C. Ngôn ngữ biên dịch – Sai.
D. Ngôn ngữ truy vấn – Sai.""",
    ),
    mcq(
        2,
        "Python được phát triển bởi ai?",
        ["Bill Gates", "James Gosling", "Guido van Rossum", "Dennis Ritchie"],
        2,
        """C. Guido van Rossum – Đúng: Người tạo Python.""",
    ),
    mcq(
        3,
        "Phần mở rộng của tệp chương trình Python thường là gì?",
        [".java", ".cpp", ".py", ".html"],
        2,
        """C. .py – Đúng.""",
    ),
    mcq(
        4,
        "Đâu là cách đặt tên biến đúng trong Python?",
        ["2diem", "diem-so", "diem_so", "diem so"],
        2,
        """C. diem_so – Đúng: hợp lệ (chữ, số, _).""",
    ),
    mcq(
        5,
        "Tên biến nào sau đây không hợp lệ trong Python?",
        ["ho_ten", "diemToan", "_diem", "10diem"],
        3,
        """D. 10diem – Sai: không bắt đầu bằng chữ số.""",
    ),
    mcq(
        6,
        "Tên biến nào sau đây hợp lệ trong Python?",
        ["ho ten", "ho-ten", "ho_ten", "ho@ten"],
        2,
        """C. ho_ten – Đúng.""",
    ),
    mcq(
        7,
        "Tên nào sau đây không thể sử dụng làm tên biến trong Python?",
        ["student", "student_name", "class", "student1"],
        2,
        """C. class – Sai: là từ khóa Python.""",
    ),
    mcq(
        8,
        "Lệnh nào dùng để hiển thị dữ liệu ra màn hình?",
        ["input()", "print()", "show()", "display()"],
        1,
        """B. print() – Đúng.""",
    ),
    mcq(
        9,
        "Lệnh nào dùng để nhập dữ liệu từ bàn phím?",
        ["get()", "scan()", "input()", "read()"],
        2,
        """C. input() – Đúng.""",
    ),
    mcq(
        10,
        "Đâu là cách gán giá trị đúng cho biến x?",
        ["x == 10", "x = 10", "int x = 10", "10 = x"],
        1,
        """B. x = 10 – Đúng: toán tử gán.""",
    ),
    mcq(
        11,
        "Giá trị 15 thuộc kiểu dữ liệu nào trong Python?",
        ["str", "float", "int", "bool"],
        2,
        """C. int – Đúng: số nguyên.""",
    ),
    mcq(
        12,
        'Giá trị "Hello Python" thuộc kiểu dữ liệu nào?',
        ["int", "str", "float", "bool"],
        1,
        """B. str – Đúng.""",
    ),
    mcq(
        13,
        "Toán tử nào dùng để tính phần dư trong Python?",
        ["/", "//", "%", "**"],
        2,
        """C. % – Đúng. Ví dụ: 10 % 3 = 1.""",
    ),
    mcq(
        14,
        "Toán tử nào được sử dụng để tính lũy thừa trong Python?",
        ["^", "**", "//", "%%"],
        1,
        """B. ** – Đúng. Ví dụ: 2 ** 3 = 8.""",
    ),
    mcq(
        15,
        "Kết quả của chương trình sau là gì?\n\na = 5\nb = 3\nprint(a + b)",
        ["2", "8", "15", "53"],
        1,
        """B. 8 – Đúng: 5 + 3 = 8.""",
    ),
    mcq(
        16,
        "Kiểu dữ liệu nào trong Python dùng để lưu một dãy nhiều phần tử và có thể thay đổi được?",
        ["tuple", "list", "str", "int"],
        1,
        """B. list – Đúng.""",
    ),
    mcq(
        17,
        "Đâu là cách tạo một danh sách (list) đúng trong Python?",
        ["ds = (1, 2, 3)", "ds = {1, 2, 3}", "ds = [1, 2, 3]", "ds = <1, 2, 3>"],
        2,
        """C. ds = [1, 2, 3] – Đúng.""",
    ),
    mcq(
        18,
        "Phần tử đầu tiên của list trong Python có chỉ số (index) là bao nhiêu?",
        ["0", "1", "-1", "2"],
        0,
        """A. 0 – Đúng: Python đếm index từ 0.""",
    ),
    mcq(
        19,
        "Phương thức nào dùng để thêm một phần tử vào cuối list?",
        ["add()", "insert()", "append()", "push()"],
        2,
        """C. append() – Đúng.""",
    ),
    mcq(
        20,
        "Từ khóa nào được sử dụng để định nghĩa một hàm trong Python?",
        ["function", "func", "def", "method"],
        2,
        """C. def – Đúng.""",
    ),
    # ── Tự luận 1: hàm max 3 số ──────────────────────────
    {
        "type": "python_code",
        "content": (
            "Câu 21 — Hàm tìm số lớn nhất trong 3 số\n\n"
            "Viết hàm max_of_three(a, b, c) trả về giá trị lớn nhất của 3 số a, b, c.\n\n"
            "Yêu cầu:\n"
            "- Định nghĩa đúng tên hàm: max_of_three\n"
            "- Hàm nhận 3 tham số và return số lớn nhất\n"
            "- Không cần dùng input()/print() — hệ thống sẽ gọi hàm để chấm\n\n"
            "Gợi ý: dùng max(a, b, c) hoặc so sánh bằng if."
        ),
        "points": 5,
        "allow_run": True,
        "function_name": "max_of_three",
        "hint": "def max_of_three(a, b, c): return max(a, b, c)",
        "starter_code": (
            "def max_of_three(a, b, c):\n"
            "    # Viet code tra ve so lon nhat\n"
            "    pass\n"
        ),
        "testcases": [
            {"name": "Ba số khác nhau", "mode": "function", "function_name": "max_of_three", "args": [1, 5, 3], "expected": 5},
            {"name": "Số âm", "mode": "function", "function_name": "max_of_three", "args": [-2, -9, -1], "expected": -1},
            {"name": "Có số bằng nhau", "mode": "function", "function_name": "max_of_three", "args": [7, 7, 2], "expected": 7},
            {"name": "Max là số đầu", "mode": "function", "function_name": "max_of_three", "args": [10, 3, 4], "expected": 10},
            {"name": "Max là số cuối", "mode": "function", "function_name": "max_of_three", "args": [0, 0, 8], "expected": 8},
        ],
        "order_num": 20,
    },
    # ── Tự luận 2: phương trình bậc nhất ─────────────────
    {
        "type": "python_code",
        "content": (
            "Câu 22 — Phương trình bậc nhất ax + b = 0\n\n"
            "Viết chương trình nhập vào 2 số a, b của phương trình bậc nhất ax + b = 0 "
            "và đưa ra nghiệm của phương trình.\n\n"
            "Giải thích: Nghiệm là giá trị của x làm phương trình bằng 0.\n"
            "Phương trình bậc nhất có dạng: a*x + b = 0\n\n"
            "Yêu cầu in kết quả (mỗi trường hợp một dòng):\n"
            "- Nếu a = 0 và b = 0  → in đúng: Vo so nghiem\n"
            "- Nếu a = 0 và b ≠ 0  → in đúng: Vo nghiem\n"
            "- Nếu a ≠ 0          → in nghiệm x = -b/a (một số)\n\n"
            "Ví dụ:\n"
            "  Nhập a=2, b=-4  → in 2.0  (vì 2x - 4 = 0 ⇒ x = 2)\n"
            "  Nhập a=0, b=5   → in Vo nghiem\n"
            "  Nhập a=0, b=0   → in Vo so nghiem"
        ),
        "points": 5,
        "allow_run": True,
        "hint": (
            "a = float(input()) ; b = float(input()). "
            "if a == 0: kiểm tra b. else: print(-b/a)"
        ),
        "starter_code": (
            'a = float(input("Nhap a: "))\n'
            'b = float(input("Nhap b: "))\n\n'
            "# Xu ly cac truong hop: vo nghiem / vo so nghiem / co nghiem\n"
        ),
        "testcases": [
            {
                "name": "Có nghiệm",
                "mode": "stdin",
                "stdin": "2\n-4\n",
                "expected_stdout": "2.0",
            },
            {
                "name": "Có nghiệm (âm)",
                "mode": "stdin",
                "stdin": "5\n10\n",
                "expected_stdout": "-2.0",
            },
            {
                "name": "Vô nghiệm",
                "mode": "stdin",
                "stdin": "0\n5\n",
                "expected_stdout": "Vo nghiem",
            },
            {
                "name": "Vô số nghiệm",
                "mode": "stdin",
                "stdin": "0\n0\n",
                "expected_stdout": "Vo so nghiem",
            },
            {
                "name": "Có nghiệm phân số",
                "mode": "stdin",
                "stdin": "4\n-2\n",
                "expected_stdout": "0.5",
            },
        ],
        "order_num": 21,
    },
]


def main():
    app = create_app()
    with app.app_context():
        questions = sanitize_questions(RAW)
        description = (
            "Bài kiểm tra Python: 20 câu trắc nghiệm lý thuyết + 2 câu tự luận viết code. "
            "Câu tự luận được chấm tự động bằng testcase khi nộp bài."
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
                        "duration_minutes": 40,
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
            # Đảm bảo slug trống
            if col("quizzes").find_one({"slug": FIXED_SLUG}):
                slug = None
                for _ in range(20):
                    candidate = generate_quiz_slug()
                    if not col("quizzes").find_one({"slug": candidate}):
                        slug = candidate
                        break
                if not slug:
                    raise RuntimeError("Không tạo được slug")
            else:
                slug = FIXED_SLUG

            doc = {
                "title": QUIZ_TITLE,
                "description": description,
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
