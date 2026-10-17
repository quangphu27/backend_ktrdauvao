"""Seed: Bài kiểm tra Python 17/10 — 15 TN (từ các đề trước) + 3 tự luận."""

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions

QUIZ_TITLE = "Bài kiểm tra Python ngày 17-10"
FIXED_SLUG = "python-1710"


def mcq(num, content, options, correct_idx, explanation=""):
    opts = [{"text": t, "is_correct": i == correct_idx} for i, t in enumerate(options)]
    return {
        "type": "mcq",
        "content": f"Câu {num}: {content}",
        "points": 2,
        "options": opts,
        "explanation": (explanation or "").strip(),
        "order_num": num - 1,
    }


def build_questions():
    # 15 TN lấy từ các đề trước (0410, 1010, 2009…) — gắn với NT / vòng lặp / menu
    questions = [
        mcq(
            1,
            "Lệnh nào dùng để nhập dữ liệu từ bàn phím trong Python?",
            ["print()", "input()", "scan()", "read()"],
            1,
            "B. input() – Đúng.",
        ),
        mcq(
            2,
            "Lệnh nào dùng để hiển thị dữ liệu ra màn hình?",
            ["input()", "print()", "show()", "display()"],
            1,
            "B. print() – Đúng.",
        ),
        mcq(
            3,
            "Giá trị 15 thuộc kiểu dữ liệu nào trong Python?",
            ["str", "float", "int", "bool"],
            2,
            "C. int – Số nguyên.",
        ),
        mcq(
            4,
            "Toán tử nào dùng để tính phần dư trong Python?",
            ["/", "//", "%", "**"],
            2,
            "C. % – Ví dụ: 10 % 3 = 1.",
        ),
        mcq(
            5,
            "Kết quả của biểu thức: 17 % 5",
            ["3", "2", "3.4", "0"],
            1,
            "B. 2 – 17 = 3×5 + 2.",
        ),
        mcq(
            6,
            "Cách nào kiểm tra n chia hết cho d?",
            ["n / d == 0", "n // d == 0", "n % d == 0", "n ** d == 0"],
            2,
            "C. n % d == 0.",
        ),
        mcq(
            7,
            "Số nào sau đây là số nguyên tố?",
            ["1", "9", "15", "13"],
            3,
            "D. 13 – Chỉ chia hết cho 1 và chính nó.",
        ),
        mcq(
            8,
            "Số nào sau đây là hợp số?",
            ["2", "3", "11", "12"],
            3,
            "D. 12 – Có ước thực sự ngoài 1 và chính nó.",
        ),
        mcq(
            9,
            "1 được xếp vào loại nào?",
            ["Số nguyên tố", "Hợp số", "Không phải nguyên tố cũng không phải hợp số", "Số chẵn"],
            2,
            "C. 1 không phải số nguyên tố và cũng không phải hợp số.",
        ),
        mcq(
            10,
            "Các ước dương của 12 là:",
            ["1, 2, 3, 4, 6, 12", "2, 3, 4, 6", "1, 12", "1, 2, 3, 12"],
            0,
            "A. 1, 2, 3, 4, 6, 12.",
        ),
        mcq(
            11,
            "Vòng lặp nào thường dùng để duyệt từng phần tử trong list?",
            ["if", "for", "class", "def"],
            1,
            "B. for – Đúng.",
        ),
        mcq(
            12,
            "Kết quả của đoạn mã?\n\nfor i in range(1, 4):\n    print(i, end=' ')",
            ["1 2 3", "1 2 3 4", "0 1 2 3", "1 2"],
            0,
            "A. range(1, 4) tạo 1, 2, 3.",
        ),
        mcq(
            13,
            "Hàm nào trả về số phần tử của list / số ký tự của chuỗi?",
            ["sum()", "max()", "len()", "count()"],
            2,
            "C. len() – Đúng.",
        ),
        mcq(
            14,
            "Dãy Fibonacci bắt đầu 1, 1, 2, 3, 5. Số tiếp theo là:",
            ["6", "7", "8", "9"],
            2,
            "C. 8 = 3 + 5.",
        ),
        mcq(
            15,
            "Để làm menu chọn chức năng chạy đến khi người dùng thoát, thường dùng:",
            ["for i in range(1)", "while True + break khi chọn thoát", "if không có else", "class Menu"],
            1,
            "B. while True và break khi chọn 0 / thoát.",
        ),
    ]

    # ── TL1: Số nguyên tố ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 16 — KIỂM TRA SỐ NGUYÊN TỐ\n\n"
            "Nhập vào 1 số nguyên N và kiểm tra xem số đó có phải số nguyên tố hay không.\n\n"
            "Quy ước: số nguyên tố là số nguyên > 1, chỉ chia hết cho 1 và chính nó.\n"
            "(Số ≤ 1 không phải số nguyên tố.)\n\n"
            "Viết hàm la_nguyen_to(n) trả về True nếu n là số nguyên tố, ngược lại False.\n\n"
            "Ví dụ:\n"
            "la_nguyen_to(13) → True\n"
            "la_nguyen_to(12) → False\n"
            "la_nguyen_to(1) → False"
        ),
        "points": 24,
        "allow_run": True,
        "function_name": "la_nguyen_to",
        "hint": (
            "if n <= 1: return False. "
            "for i in range(2, int(n**0.5)+1): if n % i == 0: return False. "
            "return True."
        ),
        "starter_code": (
            "def la_nguyen_to(n):\n"
            "    # Tra ve True neu n la so nguyen to, nguoc lai False\n"
            "    pass\n\n"
            "# Thu: print(la_nguyen_to(13))  # True\n"
            "# print(la_nguyen_to(12))  # False\n"
        ),
        "testcases": [
            {
                "name": "13 là NT",
                "mode": "function",
                "function_name": "la_nguyen_to",
                "args": [13],
                "expected": True,
            },
            {
                "name": "12 không NT",
                "mode": "function",
                "function_name": "la_nguyen_to",
                "args": [12],
                "expected": False,
            },
            {
                "name": "2 là NT",
                "mode": "function",
                "function_name": "la_nguyen_to",
                "args": [2],
                "expected": True,
            },
            {
                "name": "1 không NT",
                "mode": "function",
                "function_name": "la_nguyen_to",
                "args": [1],
                "expected": False,
            },
            {
                "name": "0 / âm không NT",
                "mode": "function",
                "function_name": "la_nguyen_to",
                "args": [0],
                "expected": False,
            },
            {
                "name": "97 là NT",
                "mode": "function",
                "function_name": "la_nguyen_to",
                "args": [97],
                "expected": True,
            },
        ],
        "order_num": 15,
    })

    # ── TL2: N số Fibonacci ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 17 — N SỐ FIBONACCI ĐẦU TIÊN\n\n"
            "Viết chương trình in ra N số Fibonacci đầu tiên, "
            "với N được nhập vào từ bàn phím.\n\n"
            "Quy ước dãy: 1, 1, 2, 3, 5, 8, ... "
            "(số sau = tổng 2 số trước; bắt đầu bằng 1, 1).\n\n"
            "Viết hàm n_fibonacci(n) trả về list gồm n số Fibonacci đầu tiên.\n\n"
            "Ví dụ:\n"
            "n_fibonacci(1) → [1]\n"
            "n_fibonacci(2) → [1, 1]\n"
            "n_fibonacci(5) → [1, 1, 2, 3, 5]\n"
            "n_fibonacci(7) → [1, 1, 2, 3, 5, 8, 13]"
        ),
        "points": 23,
        "allow_run": True,
        "function_name": "n_fibonacci",
        "hint": (
            "Nếu n <= 0: return []. "
            "Nếu n == 1: return [1]. "
            "Bắt đầu [1, 1], rồi append a+b cho đến đủ n phần tử."
        ),
        "starter_code": (
            "def n_fibonacci(n):\n"
            "    # Tra ve list n so Fibonacci dau tien (bat dau 1, 1)\n"
            "    pass\n\n"
            "# Thu: print(n_fibonacci(7))  # [1, 1, 2, 3, 5, 8, 13]\n"
        ),
        "testcases": [
            {
                "name": "n=1",
                "mode": "function",
                "function_name": "n_fibonacci",
                "args": [1],
                "expected": [1],
            },
            {
                "name": "n=2",
                "mode": "function",
                "function_name": "n_fibonacci",
                "args": [2],
                "expected": [1, 1],
            },
            {
                "name": "n=5",
                "mode": "function",
                "function_name": "n_fibonacci",
                "args": [5],
                "expected": [1, 1, 2, 3, 5],
            },
            {
                "name": "n=7",
                "mode": "function",
                "function_name": "n_fibonacci",
                "args": [7],
                "expected": [1, 1, 2, 3, 5, 8, 13],
            },
            {
                "name": "n=0 → []",
                "mode": "function",
                "function_name": "n_fibonacci",
                "args": [0],
                "expected": [],
            },
        ],
        "order_num": 16,
    })

    # ── TL3: Menu hình học ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 18 — MENU TÍNH CHU VI & DIỆN TÍCH\n\n"
            "Viết chương trình gồm các chức năng sau:\n"
            "Nhập phím 1: Tính chu vi, diện tích hình tròn\n"
            "Nhập phím 2: Tính chu vi, diện tích hình chữ nhật\n"
            "Nhập phím 3: Tính chu vi, diện tích hình tam giác theo 3 cạnh\n"
            "Nhập phím 0: Kết thúc chương trình\n\n"
            "Công thức (dùng π = 3.14):\n"
            "- Hình tròn bán kính r: chu vi = 2*π*r, diện tích = π*r*r\n"
            "- Hình chữ nhật dài a, rộng b: chu vi = 2*(a+b), diện tích = a*b\n"
            "- Hình tam giác cạnh a, b, c: chu vi = a+b+c; "
            "diện tích theo Heron: p = chu_vi/2, S = sqrt(p(p-a)(p-b)(p-c))\n"
            "  (Nếu không thỏa tam giác thì diện tích = 0)\n\n"
            "Yêu cầu chấm tự động — viết các hàm (làm tròn 2 chữ số thập phân bằng round(..., 2)):\n"
            "- hinh_tron(r) → (chu_vi, dien_tich)\n"
            "- hinh_chu_nhat(a, b) → (chu_vi, dien_tich)\n"
            "- hinh_tam_giac(a, b, c) → (chu_vi, dien_tich)\n\n"
            "Và viết vòng lặp menu (1/2/3/0) như đề — có thể bấm Chạy thử để nhập liệu.\n\n"
            "Ví dụ:\n"
            "hinh_tron(5) → (31.4, 78.5)\n"
            "hinh_chu_nhat(3, 4) → (14, 12)\n"
            "hinh_tam_giac(3, 4, 5) → (12, 6.0)"
        ),
        "points": 23,
        "allow_run": True,
        "function_name": "hinh_tron",
        "hint": (
            "PI = 3.14; return (round(2*PI*r, 2), round(PI*r*r, 2)). "
            "Tam giác: kiểm tra a+b>c và a+c>b và b+c>a; "
            "import math; S = round(math.sqrt(p*(p-a)*(p-b)*(p-c)), 2). "
            "Menu: while True + if chon == '1'/ '2'/ '3'/ '0'."
        ),
        "starter_code": (
            "import math\n\n"
            "PI = 3.14\n\n"
            "def hinh_tron(r):\n"
            "    # Tra ve (chu_vi, dien_tich) — dung round(..., 2)\n"
            "    pass\n\n"
            "def hinh_chu_nhat(a, b):\n"
            "    # Tra ve (chu_vi, dien_tich)\n"
            "    pass\n\n"
            "def hinh_tam_giac(a, b, c):\n"
            "    # Tra ve (chu_vi, dien_tich); neu khong thanh tam giac thi dien_tich = 0\n"
            "    pass\n\n"
            "# ===== MENU (viet them) =====\n"
            "# while True:\n"
            '#     print("1. Hinh tron")\n'
            '#     print("2. Hinh chu nhat")\n'
            '#     print("3. Hinh tam giac")\n'
            '#     print("0. Ket thuc")\n'
            '#     chon = input("Chon: ")\n'
            '#     if chon == "0":\n'
            "#         break\n"
            "#     ...\n"
        ),
        "testcases": [
            {
                "name": "Tròn r=5",
                "mode": "function",
                "function_name": "hinh_tron",
                "args": [5],
                "expected": [31.4, 78.5],
            },
            {
                "name": "Tròn r=1",
                "mode": "function",
                "function_name": "hinh_tron",
                "args": [1],
                "expected": [6.28, 3.14],
            },
            {
                "name": "HCN 3×4",
                "mode": "function",
                "function_name": "hinh_chu_nhat",
                "args": [3, 4],
                "expected": [14, 12],
            },
            {
                "name": "HCN 2×5",
                "mode": "function",
                "function_name": "hinh_chu_nhat",
                "args": [2, 5],
                "expected": [14, 10],
            },
            {
                "name": "TG 3-4-5",
                "mode": "function",
                "function_name": "hinh_tam_giac",
                "args": [3, 4, 5],
                "expected": [12, 6.0],
            },
            {
                "name": "TG không hợp lệ",
                "mode": "function",
                "function_name": "hinh_tam_giac",
                "args": [1, 2, 3],
                "expected": [6, 0],
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
            "Bài kiểm tra Python 17/10 — 15 câu trắc nghiệm + 3 câu tự luận: "
            "Số nguyên tố · N số Fibonacci · Menu chu vi/diện tích "
            "(tròn · chữ nhật · tam giác). Tự luận chấm bằng testcase (hàm)."
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
        mc = sum(1 for q in data["questions"] if q.get("type") == "mcq")
        tl = sum(1 for q in data["questions"] if q.get("type") == "python_code")
        pts = sum(int(q.get("points") or 0) for q in data["questions"])
        print(f"mcq={mc} code={tl} total_points={pts}")
        print(f"public=/quiz/{data['slug']}")


if __name__ == "__main__":
    main()
