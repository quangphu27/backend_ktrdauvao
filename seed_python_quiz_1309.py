"""Seed: Bài kiểm tra Python 13/09 — 15 TN (chọn câu khó, đảo thứ tự) + 2 tự luận."""

import random
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions

QUIZ_TITLE = "Bài kiểm tra Python ngày 13-09"
FIXED_SLUG = "python-1309"


def mcq(content, options, correct_idx, explanation):
    opts = [{"text": t, "is_correct": i == correct_idx} for i, t in enumerate(options)]
    return {
        "type": "mcq",
        "content": content,
        "points": 1,
        "options": opts,
        "explanation": explanation.strip(),
    }


# Ngân hàng câu khó hơn (hàm, list, OOP, file, vòng lặp, toán tử…)
HARD_MCQ_BANK = [
    mcq(
        "Tên nào sau đây không thể dùng làm tên biến trong Python?",
        ["student", "student_name", "class", "student1"],
        2,
        "C. class – Là từ khóa Python.",
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
        "B. list – Đúng (tuple không sửa được).",
    ),
    mcq(
        "Đâu là cách tạo list đúng?",
        ["ds = (1, 2, 3)", "ds = {1, 2, 3}", "ds = [1, 2, 3]", "ds = <1, 2, 3>"],
        2,
        "C. ds = [1, 2, 3] – Đúng. () là tuple, {} là set/dict.",
    ),
    mcq(
        "Phần tử đầu tiên của list có chỉ số nào?",
        ["0", "1", "-1", "2"],
        0,
        "A. 0 – Python đếm index từ 0; -1 là phần tử cuối.",
    ),
    mcq(
        "Phương thức nào thêm phần tử vào cuối list?",
        ["add()", "insert()", "append()", "push()"],
        2,
        "C. append() – Đúng. insert() thêm theo vị trí.",
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
        "Đoạn chương trình sau in ra gì?\n\ndef tong(a, b):\n    return a + b\n\nprint(tong(3, 5))",
        ["3", "5", "8", "15"],
        2,
        "C. 8 – Đúng: 3 + 5 = 8.",
    ),
    mcq(
        "Từ khóa nào tạo class trong Python?",
        ["object", "class", "struct", "new"],
        1,
        "B. class – Đúng.",
    ),
    mcq(
        "Trong OOP, class được hiểu là gì?",
        ["Một biến", "Một vòng lặp", "Một khuôn mẫu để tạo đối tượng", "Kiểu chỉ lưu số"],
        2,
        "C. Khuôn mẫu để tạo các đối tượng – Đúng.",
    ),
    mcq(
        "Dictionary lưu dữ liệu theo dạng nào?",
        ["Chỉ value", "Key : Value", "Chỉ index số", "Chỉ list"],
        1,
        "B. Key : Value – Đúng.",
    ),
    mcq(
        "Cú pháp nào đúng để tạo dictionary rỗng?",
        ["d = []", "d = ()", "d = {}", "d = <>"],
        2,
        "C. d = {} – Đúng.",
    ),
    mcq(
        "Lệnh nào mở một tệp trong Python?",
        ["open()", "file()", "read()", "load()"],
        0,
        "A. open() – Đúng.",
    ),
    mcq(
        'Chế độ nào mở tệp chỉ để đọc?',
        ['"w"', '"a"', '"r"', '"x"'],
        2,
        'C. "r" – Read.',
    ),
    mcq(
        'Chế độ nào ghi tệp và có thể xóa nội dung cũ?',
        ['"r"', '"w"', '"a"', '"read"'],
        1,
        'B. "w" – Write (ghi đè). "a" là ghi thêm.',
    ),
    mcq(
        "Vòng lặp nào thường dùng để duyệt phần tử của list?",
        ["if", "for", "class", "def"],
        1,
        "B. for – Đúng.",
    ),
    mcq(
        "Cú pháp if nào đúng trong Python?",
        ["if x > 5:", "if (x > 5)", "if x > 5 then", "if: x > 5"],
        0,
        "A. if x > 5: – Đúng (có dấu :).",
    ),
    mcq(
        "Kết quả của chương trình?\n\nfor i in range(1, 4):\n    print(i)",
        ["1 2 3", "1 2 3 4", "0 1 2 3", "0 1 2"],
        0,
        "A. 1 2 3 – range(1, 4) không lấy 4.",
    ),
    mcq(
        "Vòng lặp while tiếp tục khi nào?",
        ["Khi điều kiện còn đúng", "Khi điều kiện sai", "Chỉ một lần", "Khi chương trình kết thúc"],
        0,
        "A. Khi điều kiện còn đúng – Đúng.",
    ),
    mcq(
        "Kết quả của lệnh: print(type(3.14))",
        ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'bool'>"],
        1,
        "B. float – Đúng.",
    ),
    mcq(
        "Kết quả của biểu thức: 10 // 3",
        ["3.33", "3", "1", "30"],
        1,
        "B. 3 – // là chia lấy phần nguyên.",
    ),
    mcq(
        "Kết quả của biểu thức: 2 ** 3 ** 2\n(Gợi ý: ** kết hợp từ phải sang trái)",
        ["64", "512", "12", "36"],
        1,
        "B. 512 – 3**2=9 rồi 2**9=512.",
    ),
]


def build_questions():
    rng = random.Random(1309)
    picked = rng.sample(HARD_MCQ_BANK, 15)
    questions = []
    for i, q in enumerate(picked):
        item = dict(q)
        item["content"] = f"Câu {i + 1}: {q['content']}"
        item["order_num"] = i
        opts = list(item["options"])
        rng.shuffle(opts)
        item["options"] = opts
        questions.append(item)

    # ── Tự luận 1: Số đẹp ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 16 — SỐ ĐẸP\n\n"
            "Một số được gọi là số đẹp nếu tổng bình phương các chữ số "
            "trong biểu diễn thập phân của nó là một số nguyên tố.\n\n"
            "Ví dụ: 12 là số đẹp vì 1² + 2² = 5 là số nguyên tố.\n\n"
            "Các số đẹp được đánh số thứ tự theo giá trị tăng dần, "
            "bắt đầu từ số đẹp nhỏ nhất.\n\n"
            "Yêu cầu: Cho số nguyên N (1 ≤ N ≤ 10⁶). "
            "Tìm số đẹp thứ N.\n\n"
            "Viết hàm so_dep(n) trả về số đẹp thứ n.\n"
            "Hệ thống sẽ gọi hàm để chấm — không bắt buộc dùng input()/print()."
        ),
        "points": 5,
        "allow_run": True,
        "function_name": "so_dep",
        "hint": (
            "Viết hàm kiểm tra nguyên tố; tính tổng bình phương chữ số; "
            "duyệt x = 1, 2, 3… đếm số đẹp đến khi đủ n."
        ),
        "starter_code": (
            "def so_dep(n):\n"
            "    # Tra ve so dep thu n\n"
            "    pass\n\n"
            "# Thu: print(so_dep(1))   # 11\n"
            "# Thu: print(so_dep(2))   # 12\n"
        ),
        "testcases": [
            {
                "name": "Số đẹp thứ 1",
                "mode": "function",
                "function_name": "so_dep",
                "args": [1],
                "expected": 11,
            },
            {
                "name": "Số đẹp thứ 2 (= ví dụ 12)",
                "mode": "function",
                "function_name": "so_dep",
                "args": [2],
                "expected": 12,
            },
            {
                "name": "Số đẹp thứ 5",
                "mode": "function",
                "function_name": "so_dep",
                "args": [5],
                "expected": 21,
            },
            {
                "name": "Số đẹp thứ 10",
                "mode": "function",
                "function_name": "so_dep",
                "args": [10],
                "expected": 38,
            },
            {
                "name": "Số đẹp thứ 100",
                "mode": "function",
                "function_name": "so_dep",
                "args": [100],
                "expected": 379,
            },
        ],
        "order_num": 15,
    })

    # ── Tự luận 2: Tìm số ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 17 — TÌM SỐ\n\n"
            "Cho 2 số nguyên dương A, B (1 ≤ A < B ≤ 30000). "
            "Tìm 2 số nguyên dương p và q với p ≤ q sao cho:\n"
            "  p + q = A\n"
            "  p × q = B\n\n"
            "Viết hàm tim_so(a, b) trả về chuỗi \"p q\" (hai số cách nhau một dấu cách).\n"
            "Giả sử với bộ test luôn tồn tại đúng một cặp (p, q) thỏa mãn.\n\n"
            "Gợi ý: p, q là nghiệm của phương trình x² − A·x + B = 0 "
            "(delta = A² − 4B phải là số chính phương)."
        ),
        "points": 5,
        "allow_run": True,
        "function_name": "tim_so",
        "hint": (
            "delta = a*a - 4*b; s = int(delta**0.5); "
            "p = (a - s)//2; q = (a + s)//2; return f'{p} {q}'"
        ),
        "starter_code": (
            "def tim_so(a, b):\n"
            "    # Tim p, q: p + q = a, p * q = b, p <= q\n"
            "    # return dang chuoi: 'p q'\n"
            "    pass\n\n"
            "# Thu: print(tim_so(5, 6))    # 2 3\n"
            "# Thu: print(tim_so(10, 21))  # 3 7\n"
        ),
        "testcases": [
            {
                "name": "A=5, B=6 → 2 3",
                "mode": "function",
                "function_name": "tim_so",
                "args": [5, 6],
                "expected": "2 3",
            },
            {
                "name": "A=10, B=21 → 3 7",
                "mode": "function",
                "function_name": "tim_so",
                "args": [10, 21],
                "expected": "3 7",
            },
            {
                "name": "A=9, B=20 → 4 5",
                "mode": "function",
                "function_name": "tim_so",
                "args": [9, 20],
                "expected": "4 5",
            },
            {
                "name": "A=13, B=36 → 4 9",
                "mode": "function",
                "function_name": "tim_so",
                "args": [13, 36],
                "expected": "4 9",
            },
            {
                "name": "A=20, B=91 → 7 13",
                "mode": "function",
                "function_name": "tim_so",
                "args": [20, 91],
                "expected": "7 13",
            },
        ],
        "order_num": 16,
    })

    return questions


def main():
    app = create_app()
    with app.app_context():
        questions = sanitize_questions(build_questions())
        description = (
            "Bài kiểm tra Python 13/09 — 15 câu trắc nghiệm lý thuyết (câu khó hơn, đảo thứ tự) "
            "+ 2 câu tự luận: Số đẹp · Tìm số p, q. Tự luận chấm bằng testcase."
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
                        "duration_minutes": 60,
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
                "duration_minutes": 60,
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
