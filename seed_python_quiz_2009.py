"""Seed: Bài kiểm tra Python 20/09 — 15 TN + 3 tự luận."""

import random
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions

QUIZ_TITLE = "Bài kiểm tra Python ngày 20-09"
FIXED_SLUG = "python-2009"


def mcq(content, options, correct_idx, explanation):
    opts = [{"text": t, "is_correct": i == correct_idx} for i, t in enumerate(options)]
    return {
        "type": "mcq",
        "content": content,
        "points": 1,
        "options": opts,
        "explanation": explanation.strip(),
    }


MCQ_BANK = [
    mcq(
        "Lệnh nào dùng để nhập dữ liệu từ bàn phím?",
        ["get()", "scan()", "input()", "read()"],
        2,
        "C. input() – Đúng.",
    ),
    mcq(
        "Lệnh nào dùng để hiển thị dữ liệu ra màn hình?",
        ["input()", "print()", "show()", "display()"],
        1,
        "B. print() – Đúng.",
    ),
    mcq(
        "Kết quả của chương trình?\n\na = 5\nb = 3\nprint(a + b)",
        ["2", "8", "15", "53"],
        1,
        "B. 8 – Đúng: 5 + 3 = 8.",
    ),
    mcq(
        "Toán tử nào dùng để tính phần dư trong Python?",
        ["/", "//", "%", "**"],
        2,
        "C. % – Đúng. Ví dụ: 10 % 3 = 1.",
    ),
    mcq(
        "Kết quả của biểu thức: 10 // 3",
        ["3.33", "3", "1", "30"],
        1,
        "B. 3 – // là chia lấy phần nguyên.",
    ),
    mcq(
        "Kiểu nào lưu dãy phần tử và có thể thay đổi được?",
        ["tuple", "list", "str", "int"],
        1,
        "B. list – Đúng.",
    ),
    mcq(
        "Phương thức nào thêm phần tử vào cuối list?",
        ["add()", "insert()", "append()", "push()"],
        2,
        "C. append() – Đúng.",
    ),
    mcq(
        "Hàm nào tìm giá trị lớn nhất trong list?",
        ["max()", "min()", "sum()", "len()"],
        0,
        "A. max() – Đúng.",
    ),
    mcq(
        "Hàm nào tính tổng các phần tử trong list?",
        ["max()", "total()", "sum()", "add()"],
        2,
        "C. sum() – Đúng.",
    ),
    mcq(
        "Kết quả của: sum([10, 20, 30])",
        ["10", "30", "60", "102030"],
        2,
        "C. 60 – 10+20+30=60.",
    ),
    mcq(
        "Kết quả của: max([5, 9, 2, 7])",
        ["5", "9", "2", "7"],
        1,
        "B. 9 – Điểm/giá trị lớn nhất.",
    ),
    mcq(
        "Vòng lặp nào thường dùng để duyệt phần tử của list?",
        ["if", "for", "class", "def"],
        1,
        "B. for – Đúng.",
    ),
    mcq(
        "Cú pháp while nào đúng?",
        ["while x > 0:", "while (x > 0)", "while x > 0 then", "while: x > 0"],
        0,
        "A. while x > 0: – Có dấu hai chấm.",
    ),
    mcq(
        "Điều kiện dừng vòng lặp while nào đúng khi đọc số đến khi gặp 0?",
        ["while n != 0:", "while n == 0:", "while n > 0 only once", "while True then break never"],
        0,
        "A. while n != 0: – Tiếp tục khi n khác 0.",
    ),
    mcq(
        "Tổng chữ số của 2025 là bao nhiêu?\n(2+0+2+5)",
        ["7", "8", "9", "10"],
        2,
        "C. 9 – 2+0+2+5=9.",
    ),
    mcq(
        "Số nào chia hết cho 9?\n(Gợi ý: tổng chữ số chia hết cho 9)",
        ["2024", "2025", "2026", "2027"],
        1,
        "B. 2025 – Tổng chữ số = 9.",
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
        "Kết quả của: 9 % 9",
        ["9", "1", "0", "81"],
        2,
        "C. 0 – 9 chia hết cho 9.",
    ),
    mcq(
        "Cách chuyển chuỗi số '123' thành số nguyên?",
        ["str(123)", "int('123')", "float('abc')", "list('123')"],
        1,
        "B. int('123') – Đúng.",
    ),
    mcq(
        "Phần tử đầu tiên của list có chỉ số nào?",
        ["0", "1", "-1", "2"],
        0,
        "A. 0 – Index bắt đầu từ 0.",
    ),
    mcq(
        "Kết quả của chương trình?\n\nfor i in range(1, 4):\n    print(i)",
        ["1 2 3", "1 2 3 4", "0 1 2 3", "0 1 2"],
        0,
        "A. 1 2 3 – range(1, 4) không lấy 4.",
    ),
    mcq(
        "Đâu là cách tạo list đúng?",
        ["ds = (1, 2, 3)", "ds = {1, 2, 3}", "ds = [1, 2, 3]", "ds = <1, 2, 3>"],
        2,
        "C. ds = [1, 2, 3] – Đúng.",
    ),
    mcq(
        "Cú pháp if nào đúng trong Python?",
        ["if x > 5:", "if (x > 5)", "if x > 5 then", "if: x > 5"],
        0,
        "A. if x > 5: – Đúng.",
    ),
]


def build_questions():
    rng = random.Random(2009)
    picked = rng.sample(MCQ_BANK, 15)
    questions = []
    for i, q in enumerate(picked):
        item = dict(q)
        item["content"] = f"Câu {i + 1}: {q['content']}"
        item["order_num"] = i
        opts = list(item["options"])
        rng.shuffle(opts)
        item["options"] = opts
        questions.append(item)

    # ── TL1: Tổng tiền tiết kiệm ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 16 — TIẾT KIỆM MUA XE ĐẠP\n\n"
            "Nam bắt đầu tiết kiệm tiền để mua một chiếc xe đạp. "
            "Mỗi ngày Nam bỏ một số tiền vào hộp tiết kiệm. "
            "Cuối tuần, Nam muốn biết tổng số tiền mình đã tiết kiệm được.\n\n"
            "Cho biết số tiền Nam tiết kiệm trong N ngày. "
            "Hãy viết chương trình tính tổng số tiền Nam đã tiết kiệm.\n\n"
            "Viết hàm tong_tiet_kiem(ds) nhận vào một list số nguyên "
            "(số tiền từng ngày) và trả về tổng.\n\n"
            "Ví dụ: tong_tiet_kiem([10, 20, 15]) → 45"
        ),
        "points": 5,
        "allow_run": True,
        "function_name": "tong_tiet_kiem",
        "hint": "return sum(ds)",
        "starter_code": (
            "def tong_tiet_kiem(ds):\n"
            "    # Tinh tong so tien trong list ds\n"
            "    pass\n\n"
            "# Thu: print(tong_tiet_kiem([10, 20, 15]))  # 45\n"
        ),
        "testcases": [
            {
                "name": "3 ngày: 10+20+15",
                "mode": "function",
                "function_name": "tong_tiet_kiem",
                "args": [[10, 20, 15]],
                "expected": 45,
            },
            {
                "name": "1 ngày",
                "mode": "function",
                "function_name": "tong_tiet_kiem",
                "args": [[100]],
                "expected": 100,
            },
            {
                "name": "5 ngày",
                "mode": "function",
                "function_name": "tong_tiet_kiem",
                "args": [[5, 5, 5, 5, 5]],
                "expected": 25,
            },
            {
                "name": "Có số 0",
                "mode": "function",
                "function_name": "tong_tiet_kiem",
                "args": [[0, 50, 0, 30]],
                "expected": 80,
            },
        ],
        "order_num": 15,
    })

    # ── TL2: Điểm cao nhất ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 17 — ĐIỂM CAO NHẤT\n\n"
            "Cô giáo tổ chức một bài kiểm tra nhanh môn Tin học. "
            "Sau khi chấm bài, cô ghi điểm của tất cả học sinh vào máy tính.\n\n"
            "Cô muốn biết điểm cao nhất mà một học sinh đạt được.\n\n"
            "Cho điểm của N học sinh. Hãy tìm điểm cao nhất.\n\n"
            "Viết hàm diem_cao_nhat(ds) nhận vào một list điểm (số) "
            "và trả về điểm lớn nhất.\n\n"
            "Ví dụ: diem_cao_nhat([7, 9, 8, 10, 6]) → 10"
        ),
        "points": 5,
        "allow_run": True,
        "function_name": "diem_cao_nhat",
        "hint": "return max(ds)",
        "starter_code": (
            "def diem_cao_nhat(ds):\n"
            "    # Tra ve diem cao nhat trong list ds\n"
            "    pass\n\n"
            "# Thu: print(diem_cao_nhat([7, 9, 8, 10, 6]))  # 10\n"
        ),
        "testcases": [
            {
                "name": "Điểm 10 là cao nhất",
                "mode": "function",
                "function_name": "diem_cao_nhat",
                "args": [[7, 9, 8, 10, 6]],
                "expected": 10,
            },
            {
                "name": "Tất cả bằng nhau",
                "mode": "function",
                "function_name": "diem_cao_nhat",
                "args": [[8, 8, 8]],
                "expected": 8,
            },
            {
                "name": "Một học sinh",
                "mode": "function",
                "function_name": "diem_cao_nhat",
                "args": [[5]],
                "expected": 5,
            },
            {
                "name": "Điểm cao ở đầu",
                "mode": "function",
                "function_name": "diem_cao_nhat",
                "args": [[9.5, 7, 8, 6]],
                "expected": 9.5,
            },
        ],
        "order_num": 16,
    })

    # ── TL3: Vé may mắn (tổng chữ số % 9 == 0), lặp đến 0 ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 18 — VÉ MAY MẮN\n\n"
            "Trong một chương trình bốc thăm của trường, mỗi học sinh được phát "
            "một vé có mã số là một số nguyên dương.\n\n"
            "Ban tổ chức quy định một chiếc vé là vé may mắn nếu "
            "tổng các chữ số của mã vé chia hết cho 9.\n\n"
            "Ví dụ, mã 2025 có: 2 + 0 + 2 + 5 = 9 nên đây là vé may mắn.\n\n"
            "Hãy viết chương trình nhập vào các số (mỗi số một dòng) và đưa ra "
            "kết quả xem số đó có phải số may mắn hay không.\n\n"
            "Quy ước in kết quả:\n"
            "- Nếu may mắn: in đúng chữ May man\n"
            "- Nếu không: in đúng chữ Khong may man\n\n"
            "Lưu ý: chương trình chạy liên tục cho đến khi người dùng nhập số 0 "
            "(không in gì cho số 0)."
        ),
        "points": 5,
        "allow_run": True,
        "hint": (
            "n = int(input()); "
            "while n != 0: "
            "tong = sum(int(c) for c in str(n)); "
            "print('May man' if tong % 9 == 0 else 'Khong may man'); "
            "n = int(input())"
        ),
        "starter_code": (
            "# Doc so lien tuc den khi gap 0\n"
            "# Neu tong chu so chia het cho 9 -> print('May man')\n"
            "# Nguoc lai -> print('Khong may man')\n"
            "# Khong in gi khi nhap 0\n\n"
        ),
        "testcases": [
            {
                "name": "2025 may mắn rồi dừng",
                "mode": "stdin",
                "stdin": "2025\n0\n",
                "expected_stdout": "May man",
            },
            {
                "name": "10 không may mắn",
                "mode": "stdin",
                "stdin": "10\n0\n",
                "expected_stdout": "Khong may man",
            },
            {
                "name": "Nhiều số rồi 0",
                "mode": "stdin",
                "stdin": "2025\n18\n10\n9\n0\n",
                "expected_stdout": "May man\nMay man\nKhong may man\nMay man",
            },
            {
                "name": "Chỉ nhập 0",
                "mode": "stdin",
                "stdin": "0\n",
                "expected_stdout": "",
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
            "Bài kiểm tra Python 20/09 — 15 câu trắc nghiệm + 3 câu tự luận: "
            "Tổng tiết kiệm · Điểm cao nhất · Vé may mắn (lặp đến 0). "
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
