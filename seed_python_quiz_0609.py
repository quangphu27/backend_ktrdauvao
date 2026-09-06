"""Seed: Bài tập Python 06/09 — 15 TN (tráo thứ tự) + 3 tự luận code."""

import random
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions

QUIZ_TITLE = "Bài tập Python ngày 06-09"
FIXED_SLUG = "python-0609"


def mcq(content, options, correct_idx, explanation):
    opts = [{"text": t, "is_correct": i == correct_idx} for i, t in enumerate(options)]
    return {
        "type": "mcq",
        "content": content,
        "points": 1,
        "options": opts,
        "explanation": explanation.strip(),
    }


# Ngân hàng lý thuyết — lấy 15 câu rồi xáo với seed cố định
MCQ_BANK = [
    mcq(
        "Python là loại ngôn ngữ lập trình nào?",
        ["Ngôn ngữ máy", "Ngôn ngữ thông dịch", "Ngôn ngữ biên dịch", "Ngôn ngữ truy vấn"],
        1,
        "B. Ngôn ngữ thông dịch – Đúng.",
    ),
    mcq(
        "Python được phát triển bởi ai?",
        ["Bill Gates", "James Gosling", "Guido van Rossum", "Dennis Ritchie"],
        2,
        "C. Guido van Rossum – Đúng.",
    ),
    mcq(
        "Phần mở rộng của tệp chương trình Python thường là gì?",
        [".java", ".cpp", ".py", ".html"],
        2,
        "C. .py – Đúng.",
    ),
    mcq(
        "Đâu là cách đặt tên biến đúng trong Python?",
        ["2diem", "diem-so", "diem_so", "diem so"],
        2,
        "C. diem_so – Đúng.",
    ),
    mcq(
        "Tên biến nào sau đây không hợp lệ trong Python?",
        ["ho_ten", "diemToan", "_diem", "10diem"],
        3,
        "D. 10diem – Không bắt đầu bằng chữ số.",
    ),
    mcq(
        "Tên nào sau đây không thể dùng làm tên biến trong Python?",
        ["student", "student_name", "class", "student1"],
        2,
        "C. class – Là từ khóa Python.",
    ),
    mcq(
        "Lệnh nào dùng để hiển thị dữ liệu ra màn hình?",
        ["input()", "print()", "show()", "display()"],
        1,
        "B. print() – Đúng.",
    ),
    mcq(
        "Lệnh nào dùng để nhập dữ liệu từ bàn phím?",
        ["get()", "scan()", "input()", "read()"],
        2,
        "C. input() – Đúng.",
    ),
    mcq(
        "Đâu là cách gán giá trị đúng cho biến x?",
        ["x == 10", "x = 10", "int x = 10", "10 = x"],
        1,
        "B. x = 10 – Đúng.",
    ),
    mcq(
        "Giá trị 15 thuộc kiểu dữ liệu nào trong Python?",
        ["str", "float", "int", "bool"],
        2,
        "C. int – Đúng.",
    ),
    mcq(
        'Giá trị "Hello Python" thuộc kiểu dữ liệu nào?',
        ["int", "str", "float", "bool"],
        1,
        "B. str – Đúng.",
    ),
    mcq(
        "Toán tử nào dùng để tính phần dư trong Python?",
        ["/", "//", "%", "**"],
        2,
        "C. % – Đúng. Ví dụ: 10 % 3 = 1.",
    ),
    mcq(
        "Toán tử nào dùng để tính lũy thừa trong Python?",
        ["^", "**", "//", "%%"],
        1,
        "B. ** – Đúng. Ví dụ: 2 ** 3 = 8.",
    ),
    mcq(
        "Kết quả của chương trình?\n\na = 5\nb = 3\nprint(a + b)",
        ["2", "8", "15", "53"],
        1,
        "B. 8 – Đúng: 5 + 3 = 8.",
    ),
    mcq(
        "Kiểu nào lưu dãy phần tử và có thể thay đổi được?",
        ["tuple", "list", "str", "int"],
        1,
        "B. list – Đúng.",
    ),
    mcq(
        "Đâu là cách tạo list đúng?",
        ["ds = (1, 2, 3)", "ds = {1, 2, 3}", "ds = [1, 2, 3]", "ds = <1, 2, 3>"],
        2,
        "C. ds = [1, 2, 3] – Đúng.",
    ),
    mcq(
        "Phần tử đầu tiên của list có chỉ số nào?",
        ["0", "1", "-1", "2"],
        0,
        "A. 0 – Python đếm index từ 0.",
    ),
    mcq(
        "Phương thức nào thêm phần tử vào cuối list?",
        ["add()", "insert()", "append()", "push()"],
        2,
        "C. append() – Đúng.",
    ),
    mcq(
        "Từ khóa nào định nghĩa hàm trong Python?",
        ["function", "func", "def", "method"],
        2,
        "C. def – Đúng.",
    ),
    mcq(
        "Từ khóa nào trả về giá trị từ hàm?",
        ["return", "output", "send", "result"],
        0,
        "A. return – Đúng.",
    ),
    mcq(
        "Từ khóa nào tạo class trong Python?",
        ["object", "class", "struct", "new"],
        1,
        "B. class – Đúng.",
    ),
    mcq(
        "Dictionary lưu dữ liệu theo dạng nào?",
        ["Chỉ value", "Key : Value", "Chỉ index số", "Chỉ list"],
        1,
        "B. Key : Value – Đúng.",
    ),
]


def build_questions():
    rng = random.Random(609)  # cố định — mỗi lần seed cùng thứ tự xáo
    picked = rng.sample(MCQ_BANK, 15)
    questions = []
    for i, q in enumerate(picked):
        item = dict(q)
        item["content"] = f"Câu {i + 1}: {q['content']}"
        item["order_num"] = i
        # Xáo đáp án trong từng câu (giữ đúng is_correct)
        opts = list(item["options"])
        rng.shuffle(opts)
        item["options"] = opts
        questions.append(item)

    # ── Tự luận 1: PT bậc nhất ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 16 — Phương trình bậc nhất ax + b = 0\n\n"
            "Viết chương trình nhập vào 2 số a, b của phương trình bậc nhất ax + b = 0 "
            "và tìm nghiệm của phương trình.\n\n"
            "Giải thích: Nghiệm là giá trị của x làm phương trình đúng bằng 0.\n\n"
            "Các trường hợp:\n"
            "- a = 0 và b = 0  → in: Vo so nghiem\n"
            "- a = 0 và b ≠ 0  → in: Vo nghiem\n"
            "- a ≠ 0          → in nghiệm x = -b/a (một số)\n\n"
            "Ví dụ: a=2, b=-4 → in 2.0"
        ),
        "points": 5,
        "allow_run": True,
        "hint": "if a == 0: kiểm tra b. else: print(-b/a)",
        "starter_code": (
            'a = float(input("Nhap a: "))\n'
            'b = float(input("Nhap b: "))\n\n'
            "# Xu ly: Vo nghiem / Vo so nghiem / co nghiem\n"
        ),
        "testcases": [
            {"name": "Có nghiệm", "mode": "stdin", "stdin": "2\n-4\n", "expected_stdout": "2.0"},
            {"name": "Có nghiệm (âm)", "mode": "stdin", "stdin": "5\n10\n", "expected_stdout": "-2.0"},
            {"name": "Vô nghiệm", "mode": "stdin", "stdin": "0\n5\n", "expected_stdout": "Vo nghiem"},
            {"name": "Vô số nghiệm", "mode": "stdin", "stdin": "0\n0\n", "expected_stdout": "Vo so nghiem"},
            {"name": "Nghiệm phân số", "mode": "stdin", "stdin": "4\n-2\n", "expected_stdout": "0.5"},
        ],
        "order_num": 15,
    })

    # ── Tự luận 2: Số thiếu ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 17 — Tìm số thiếu trong danh sách tăng dần\n\n"
            "Cho danh sách tăng dần bị thiếu đúng 1 số.\n"
            "Ví dụ: ds = [1, 2, 3, 4, 6, 7, 8, 9] → số thiếu là 5.\n\n"
            "Viết hàm find_missing(ds) trả về số bị thiếu.\n\n"
            "Gợi ý:\n"
            "Cách 1: Dùng vòng lặp so sánh phần tử liền kề.\n"
            "Cách 2: Tổng đủ − tổng thiếu = số cần tìm "
            "(n = len(ds) + 1; tổng đủ = n*(n+1)//2)."
        ),
        "points": 5,
        "allow_run": True,
        "function_name": "find_missing",
        "hint": "n = len(ds) + 1; return n*(n+1)//2 - sum(ds)",
        "starter_code": (
            "def find_missing(ds):\n"
            "    # Tim so bi thieu trong danh sach tang dan\n"
            "    pass\n\n"
            "# Thu: print(find_missing([1, 2, 3, 4, 6, 7, 8, 9]))  # 5\n"
        ),
        "testcases": [
            {
                "name": "Ví dụ đề — thiếu 5",
                "mode": "function",
                "function_name": "find_missing",
                "args": [[1, 2, 3, 4, 6, 7, 8, 9]],
                "expected": 5,
            },
            {
                "name": "Thiếu ở giữa",
                "mode": "function",
                "function_name": "find_missing",
                "args": [[1, 2, 4, 5]],
                "expected": 3,
            },
            {
                "name": "Thiếu số 1",
                "mode": "function",
                "function_name": "find_missing",
                "args": [[2, 3, 4, 5]],
                "expected": 1,
            },
            {
                "name": "Thiếu số cuối",
                "mode": "function",
                "function_name": "find_missing",
                "args": [[1, 2, 3, 4, 5, 6, 7, 8, 9]],
                "expected": 10,
            },
        ],
        "order_num": 16,
    })

    # ── Tự luận 3: Class HOCSINH ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 18 — Class HOCSINH\n\n"
            "Tạo class HOCSINH có các thuộc tính:\n"
            "ten, lop, diemtoan, diemly, diemhoa\n\n"
            "Tạo phương thức XetLoaiHocSinh() để xếp loại theo điểm trung bình "
            "của 3 môn (Toán, Lý, Hóa):\n"
            "- Điểm TB > 8  → trả về: Gioi\n"
            "- Điểm TB > 7  → trả về: Kha\n"
            "- Còn lại      → trả về: Trung Binh\n\n"
            "Lưu ý: dùng đúng tên class HOCSINH và method XetLoaiHocSinh "
            "(return chuỗi như trên, không cần print)."
        ),
        "points": 5,
        "allow_run": True,
        "hint": (
            "tb = (self.diemtoan + self.diemly + self.diemhoa) / 3. "
            "if tb > 8: return 'Gioi' ..."
        ),
        "starter_code": (
            "class HOCSINH:\n"
            "    def __init__(self, ten, lop, diemtoan, diemly, diemhoa):\n"
            "        self.ten = ten\n"
            "        self.lop = lop\n"
            "        self.diemtoan = diemtoan\n"
            "        self.diemly = diemly\n"
            "        self.diemhoa = diemhoa\n"
            "\n"
            "    def XetLoaiHocSinh(self):\n"
            "        # Tinh diem TB va return 'Gioi' / 'Kha' / 'Trung Binh'\n"
            "        pass\n"
            "\n"
            "# Thu nghiem:\n"
            "# hs = HOCSINH('An', '8A', 9, 8.5, 8)\n"
            "# print(hs.XetLoaiHocSinh())\n"
        ),
        "testcases": [
            {
                "name": "Giỏi (TB > 8)",
                "mode": "class_method",
                "class_name": "HOCSINH",
                "constructor_args": ["An", "8A", 9, 9, 9],
                "method": "XetLoaiHocSinh",
                "method_args": [],
                "expected": "Gioi",
            },
            {
                "name": "Khá (7 < TB ≤ 8)",
                "mode": "class_method",
                "class_name": "HOCSINH",
                "constructor_args": ["Binh", "8A", 8, 7.5, 7.5],
                "method": "XetLoaiHocSinh",
                "method_args": [],
                "expected": "Kha",
            },
            {
                "name": "Trung Bình (TB ≤ 7)",
                "mode": "class_method",
                "class_name": "HOCSINH",
                "constructor_args": ["Cuong", "8B", 6, 6, 6],
                "method": "XetLoaiHocSinh",
                "method_args": [],
                "expected": "Trung Binh",
            },
            {
                "name": "Biên TB vừa trên 8",
                "mode": "class_method",
                "class_name": "HOCSINH",
                "constructor_args": ["Dung", "8A", 8.5, 8, 8],
                "method": "XetLoaiHocSinh",
                "method_args": [],
                "expected": "Gioi",
            },
        ],
        "order_num": 17,
    })

    return questions


def main():
    app = create_app()
    with app.app_context():
        questions = sanitize_questions(build_questions())
        description = (
            "Bài tập Python 06/09 — 15 câu trắc nghiệm lý thuyết (thứ tự đã xáo) "
            "+ 3 câu tự luận: PT bậc nhất · Số thiếu · Class HOCSINH. "
            "Tự luận chấm bằng testcase."
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
        print(f"public=/quiz/{data['slug']}")


if __name__ == "__main__":
    main()
