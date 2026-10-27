"""Seed: Bài kiểm tra Python 24/10 — 15 TN (từ các đề trước) + 3 tự luận."""

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions

QUIZ_TITLE = "Bài kiểm tra Python ngày 24-10"
FIXED_SLUG = "python-2410"


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
    # 15 TN lấy từ đề 17/10 (input / print / kiểu dữ liệu / vòng lặp / %)
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
            "Toán tử nào dùng để tính lũy thừa trong Python?",
            ["^", "**", "//", "pow+"],
            1,
            "B. ** – Ví dụ: 2 ** 3 = 8.",
        ),
        mcq(
            15,
            "Để làm menu chọn chức năng chạy đến khi người dùng thoát, thường dùng:",
            ["for i in range(1)", "while True + break khi chọn thoát", "if không có else", "class Menu"],
            1,
            "B. while True và break khi chọn 0 / thoát.",
        ),
    ]

    questions.append({
        "type": "python_code",
        "content": (
            "Câu 16 — TỔNG BÌNH PHƯƠNG\n\n"
            "Tính tổng S = 1² + 2² + ... + n²\n"
            "với n được nhập vào từ bàn phím (n là số nguyên dương).\n\n"
            "Viết hàm tong_binh_phuong(n) trả về S.\n\n"
            "Ví dụ:\n"
            "tong_binh_phuong(1) → 1\n"
            "tong_binh_phuong(3) → 14   (1 + 4 + 9)\n"
            "tong_binh_phuong(5) → 55   (1 + 4 + 9 + 16 + 25)"
        ),
        "points": 23,
        "allow_run": True,
        "function_name": "tong_binh_phuong",
        "hint": (
            "S = 0; for i in range(1, n+1): S += i*i; return S. "
            "Hoặc dùng công thức n*(n+1)*(2*n+1)//6."
        ),
        "starter_code": (
            "def tong_binh_phuong(n):\n"
            "    # Tra ve S = 1^2 + 2^2 + ... + n^2\n"
            "    pass\n\n"
            "# Thu: print(tong_binh_phuong(5))  # 55\n"
        ),
        "testcases": [
            {"name": "n=1", "mode": "function", "function_name": "tong_binh_phuong", "args": [1], "expected": 1},
            {"name": "n=3", "mode": "function", "function_name": "tong_binh_phuong", "args": [3], "expected": 14},
            {"name": "n=5", "mode": "function", "function_name": "tong_binh_phuong", "args": [5], "expected": 55},
            {"name": "n=10", "mode": "function", "function_name": "tong_binh_phuong", "args": [10], "expected": 385},
            {"name": "n=0 → 0", "mode": "function", "function_name": "tong_binh_phuong", "args": [0], "expected": 0},
        ],
        "order_num": 15,
    })

    questions.append({
        "type": "python_code",
        "content": (
            "Câu 17 — TỔNG TÍCH HAI SỐ LIỀN NHAU\n\n"
            "Tính tổng S = 1×2 + 2×3 + 3×4 + ... + (n-1)×n\n"
            "với n được nhập vào từ bàn phím (n là số nguyên, n ≥ 1).\n\n"
            "Viết hàm tong_tich_lien_tiep(n) trả về S.\n"
            "Quy ước: nếu n ≤ 1 thì S = 0 (không có số hạng).\n\n"
            "Ví dụ:\n"
            "tong_tich_lien_tiep(2) → 2        (1×2)\n"
            "tong_tich_lien_tiep(4) → 20       (1×2 + 2×3 + 3×4)\n"
            "tong_tich_lien_tiep(5) → 40       (1×2 + 2×3 + 3×4 + 4×5)"
        ),
        "points": 23,
        "allow_run": True,
        "function_name": "tong_tich_lien_tiep",
        "hint": (
            "S = 0; for i in range(1, n): S += i * (i+1); return S."
        ),
        "starter_code": (
            "def tong_tich_lien_tiep(n):\n"
            "    # Tra ve S = 1*2 + 2*3 + ... + (n-1)*n\n"
            "    pass\n\n"
            "# Thu: print(tong_tich_lien_tiep(5))  # 40\n"
        ),
        "testcases": [
            {"name": "n=1 → 0", "mode": "function", "function_name": "tong_tich_lien_tiep", "args": [1], "expected": 0},
            {"name": "n=2", "mode": "function", "function_name": "tong_tich_lien_tiep", "args": [2], "expected": 2},
            {"name": "n=4", "mode": "function", "function_name": "tong_tich_lien_tiep", "args": [4], "expected": 20},
            {"name": "n=5", "mode": "function", "function_name": "tong_tich_lien_tiep", "args": [5], "expected": 40},
            {"name": "n=6", "mode": "function", "function_name": "tong_tich_lien_tiep", "args": [6], "expected": 70},
        ],
        "order_num": 16,
    })

    questions.append({
        "type": "python_code",
        "content": (
            "Câu 18 — MÁY TÍNH ĐƠN GIẢN\n\n"
            "Viết chương trình máy tính gồm các chức năng:\n"
            "1. Cộng 2 số\n"
            "2. Trừ 2 số\n"
            "3. Tích 2 số\n"
            "4. Thương 2 số (in số dư nếu có)\n"
            "5. Lũy thừa\n"
            "0. Kết thúc chương trình\n\n"
            "Yêu cầu chấm tự động — viết các hàm:\n"
            "- cong(a, b) → a + b\n"
            "- tru(a, b) → a - b\n"
            "- tich(a, b) → a * b\n"
            "- thuong(a, b) → (phần nguyên a//b, số dư a%b)\n"
            "  (Giả sử b ≠ 0)\n"
            "- luy_thua(a, b) → a ** b\n\n"
            "Và viết vòng lặp menu (1/2/3/4/5/0) — có thể bấm Chạy thử để nhập liệu.\n\n"
            "Ví dụ:\n"
            "cong(3, 5) → 8\n"
            "tru(10, 3) → 7\n"
            "tich(4, 6) → 24\n"
            "thuong(17, 5) → (3, 2)\n"
            "luy_thua(2, 5) → 32"
        ),
        "points": 24,
        "allow_run": True,
        "function_name": "cong",
        "hint": (
            "cong/tru/tich dùng +, -, *. "
            "thuong: return (a // b, a % b). "
            "luy_thua: return a ** b. "
            "Menu: while True + if chon == '1'..'5' / '0'."
        ),
        "starter_code": (
            "def cong(a, b):\n"
            "    pass\n\n"
            "def tru(a, b):\n"
            "    pass\n\n"
            "def tich(a, b):\n"
            "    pass\n\n"
            "def thuong(a, b):\n"
            "    # Tra ve (phan nguyen, so du) — a//b va a%b\n"
            "    pass\n\n"
            "def luy_thua(a, b):\n"
            "    pass\n\n"
            "# ===== MENU (viet them) =====\n"
            "# while True:\n"
            '#     print("1. Cong")\n'
            '#     print("2. Tru")\n'
            '#     print("3. Tich")\n'
            '#     print("4. Thuong (co so du)")\n'
            '#     print("5. Luy thua")\n'
            '#     print("0. Ket thuc")\n'
            '#     chon = input("Chon: ")\n'
            '#     if chon == "0":\n'
            "#         break\n"
            "#     ...\n"
        ),
        "testcases": [
            {"name": "Cộng 3+5", "mode": "function", "function_name": "cong", "args": [3, 5], "expected": 8},
            {"name": "Trừ 10-3", "mode": "function", "function_name": "tru", "args": [10, 3], "expected": 7},
            {"name": "Tích 4×6", "mode": "function", "function_name": "tich", "args": [4, 6], "expected": 24},
            {"name": "Thương 17÷5", "mode": "function", "function_name": "thuong", "args": [17, 5], "expected": [3, 2]},
            {"name": "Thương hết 10÷2", "mode": "function", "function_name": "thuong", "args": [10, 2], "expected": [5, 0]},
            {"name": "Lũy thừa 2^5", "mode": "function", "function_name": "luy_thua", "args": [2, 5], "expected": 32},
            {"name": "Lũy thừa 3^0", "mode": "function", "function_name": "luy_thua", "args": [3, 0], "expected": 1},
        ],
        "order_num": 17,
    })

    return questions


def main():
    app = create_app()
    with app.app_context():
        questions = sanitize_questions(build_questions())
        description = (
            "Bài kiểm tra Python 24/10 — 15 câu trắc nghiệm + 3 câu tự luận: "
            "Tổng bình phương · Tổng tích liền nhau · Máy tính đơn giản "
            "(cộng · trừ · tích · thương có dư · lũy thừa). Tự luận chấm bằng testcase (hàm)."
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
