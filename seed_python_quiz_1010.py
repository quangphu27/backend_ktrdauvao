"""Seed: Bài kiểm tra Python 10/10 — 15 TN (từ các đề trước) + 5 tự luận."""

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions

QUIZ_TITLE = "Bài kiểm tra Python ngày 10-10"
FIXED_SLUG = "python-1010"


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
    # 15 TN lấy / chỉnh từ các đề trước (chuỗi, số, vòng lặp — khớp tự luận)
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
            'Giá trị "Hello Python" thuộc kiểu dữ liệu nào?',
            ["int", "str", "float", "bool"],
            1,
            "B. str – Chuỗi ký tự.",
        ),
        mcq(
            4,
            "Giá trị 15 thuộc kiểu dữ liệu nào trong Python?",
            ["str", "float", "int", "bool"],
            2,
            "C. int – Số nguyên.",
        ),
        mcq(
            5,
            "Toán tử nào dùng để tính phần dư trong Python?",
            ["/", "//", "%", "**"],
            2,
            "C. % – Ví dụ: 10 % 3 = 1.",
        ),
        mcq(
            6,
            "Kết quả của biểu thức: 17 % 5",
            ["3", "2", "3.4", "0"],
            1,
            "B. 2 – 17 = 3×5 + 2.",
        ),
        mcq(
            7,
            "Phương thức nào viết hoa toàn bộ chuỗi s?",
            ["s.lower()", "s.upper()", "s.title()", "s.capitalize()"],
            1,
            "B. s.upper() – Đúng.",
        ),
        mcq(
            8,
            'Kết quả của: "lap trinh".upper()',
            ["Lap Trinh", "LAP TRINH", "lap trinh", "Lap trinh"],
            1,
            "B. LAP TRINH.",
        ),
        mcq(
            9,
            'Để tách câu thành các từ, dùng:',
            ['s.split()', 's.join()', 's.strip()', 's.replace()'],
            0,
            "A. s.split() – Tách theo khoảng trắng (mặc định).",
        ),
        mcq(
            10,
            'Số từ trong câu "Em hoc Python rat vui" (tách theo khoảng trắng) là:',
            ["4", "5", "6", "3"],
            1,
            "B. 5 từ.",
        ),
        mcq(
            11,
            "Hàm nào trả về số phần tử của list / số ký tự của chuỗi?",
            ["sum()", "max()", "len()", "count()"],
            2,
            "C. len() – Đúng.",
        ),
        mcq(
            12,
            "Vòng lặp nào thường dùng để duyệt từng phần tử trong list?",
            ["if", "for", "class", "def"],
            1,
            "B. for – Đúng.",
        ),
        mcq(
            13,
            "Các ước dương của 12 là:",
            ["1, 2, 3, 4, 6, 12", "2, 3, 4, 6", "1, 12", "1, 2, 3, 12"],
            0,
            "A. 1, 2, 3, 4, 6, 12.",
        ),
        mcq(
            14,
            "Số hoàn hảo là số bằng tổng các ước dương của nó (không kể chính nó). Số nào là số hoàn hảo?",
            ["4", "6", "8", "10"],
            1,
            "B. 6 = 1 + 2 + 3.",
        ),
        mcq(
            15,
            "Khi tìm tất cả ước của n, vòng lặp thường chạy i từ:",
            ["1 đến n", "0 đến n", "2 đến n-1", "n đến 2n"],
            0,
            "A. i từ 1 đến n (hoặc tối ưu đến căn bậc hai).",
        ),
    ]

    # ── TL1: Số thập phân → phân số tối giản ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 16 — PHÂN SỐ TỐI GIẢN\n\n"
            "Nhập vào một số thập phân và biểu diễn số đó dưới dạng phân số tối giản.\n\n"
            "Viết hàm phan_so_toi_gian(x) nhận số thực x, "
            "trả về chuỗi dạng \"tử/mẫu\" với phân số tối giản "
            "(mẫu > 0).\n\n"
            "Ví dụ:\n"
            "phan_so_toi_gian(0.75) → \"3/4\"\n"
            "phan_so_toi_gian(2.5) → \"5/2\"\n"
            "phan_so_toi_gian(0.125) → \"1/8\""
        ),
        "points": 14,
        "allow_run": True,
        "function_name": "phan_so_toi_gian",
        "hint": (
            "Dùng from fractions import Fraction rồi Fraction(str(x)) "
            "(tránh lỗi làm tròn float). Trả về f\"{tu}/{mau}\"."
        ),
        "starter_code": (
            "from fractions import Fraction\n\n"
            "def phan_so_toi_gian(x):\n"
            "    # Goi y: f = Fraction(str(x)).limit_denominator()\n"
            "    # return f\"{f.numerator}/{f.denominator}\"\n"
            "    pass\n\n"
            "# Thu: print(phan_so_toi_gian(0.75))  # 3/4\n"
        ),
        "testcases": [
            {
                "name": "0.75 → 3/4",
                "mode": "function",
                "function_name": "phan_so_toi_gian",
                "args": [0.75],
                "expected": "3/4",
            },
            {
                "name": "2.5 → 5/2",
                "mode": "function",
                "function_name": "phan_so_toi_gian",
                "args": [2.5],
                "expected": "5/2",
            },
            {
                "name": "0.125 → 1/8",
                "mode": "function",
                "function_name": "phan_so_toi_gian",
                "args": [0.125],
                "expected": "1/8",
            },
            {
                "name": "3.0 → 3/1",
                "mode": "function",
                "function_name": "phan_so_toi_gian",
                "args": [3.0],
                "expected": "3/1",
            },
            {
                "name": "-0.5 → -1/2",
                "mode": "function",
                "function_name": "phan_so_toi_gian",
                "args": [-0.5],
                "expected": "-1/2",
            },
        ],
        "order_num": 15,
    })

    # ── TL2: Viết hoa ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 17 — VIẾT HOA TOÀN BỘ CHUỖI\n\n"
            "Nhập một chuỗi, in ra chuỗi viết hoa toàn bộ.\n\n"
            "Viết hàm viet_hoa(s) trả về chuỗi đã viết hoa.\n\n"
            "Ví dụ: viet_hoa(\"lap trinh python\") → \"LAP TRINH PYTHON\""
        ),
        "points": 14,
        "allow_run": True,
        "function_name": "viet_hoa",
        "hint": "return s.upper()",
        "starter_code": (
            "def viet_hoa(s):\n"
            "    # Tra ve chuoi viet hoa toan bo\n"
            "    pass\n\n"
            "# Thu: print(viet_hoa(\"lap trinh python\"))\n"
        ),
        "testcases": [
            {
                "name": "lap trinh python",
                "mode": "function",
                "function_name": "viet_hoa",
                "args": ["lap trinh python"],
                "expected": "LAP TRINH PYTHON",
            },
            {
                "name": "Đã hoa sẵn",
                "mode": "function",
                "function_name": "viet_hoa",
                "args": ["PYTHON"],
                "expected": "PYTHON",
            },
            {
                "name": "Hỗn hợp",
                "mode": "function",
                "function_name": "viet_hoa",
                "args": ["Em Hoc Python"],
                "expected": "EM HOC PYTHON",
            },
            {
                "name": "Chuỗi rỗng",
                "mode": "function",
                "function_name": "viet_hoa",
                "args": [""],
                "expected": "",
            },
        ],
        "order_num": 16,
    })

    # ── TL3: Đếm từ ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 18 — ĐẾM SỐ TỪ TRONG CÂU\n\n"
            "Nhập một câu, đếm số từ trong câu đó.\n\n"
            "Viết hàm dem_tu(s) trả về số nguyên là số từ "
            "(tách theo khoảng trắng, bỏ qua khoảng trắng thừa).\n\n"
            "Ví dụ: dem_tu(\"Em hoc Python rat vui\") → 5"
        ),
        "points": 14,
        "allow_run": True,
        "function_name": "dem_tu",
        "hint": "return len(s.split())",
        "starter_code": (
            "def dem_tu(s):\n"
            "    # Tra ve so tu trong cau\n"
            "    pass\n\n"
            "# Thu: print(dem_tu(\"Em hoc Python rat vui\"))  # 5\n"
        ),
        "testcases": [
            {
                "name": "5 từ",
                "mode": "function",
                "function_name": "dem_tu",
                "args": ["Em hoc Python rat vui"],
                "expected": 5,
            },
            {
                "name": "1 từ",
                "mode": "function",
                "function_name": "dem_tu",
                "args": ["Python"],
                "expected": 1,
            },
            {
                "name": "Khoảng trắng thừa",
                "mode": "function",
                "function_name": "dem_tu",
                "args": ["  xin   chao  ban  "],
                "expected": 3,
            },
            {
                "name": "Chuỗi rỗng / chỉ khoảng trắng",
                "mode": "function",
                "function_name": "dem_tu",
                "args": ["   "],
                "expected": 0,
            },
        ],
        "order_num": 17,
    })

    # ── TL4: Từ dài nhất ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 19 — TỪ CÓ NHIỀU KÝ TỰ NHẤT\n\n"
            "Nhập một câu gồm nhiều từ, tìm và in ra từ có nhiều ký tự nhất.\n\n"
            "Nếu có nhiều từ cùng độ dài lớn nhất, trả về từ xuất hiện trước nhất.\n\n"
            "Viết hàm tu_dai_nhat(s) trả về từ đó.\n\n"
            "Ví dụ: tu_dai_nhat(\"Em yeu lap trinh Python\") → \"Python\""
        ),
        "points": 14,
        "allow_run": True,
        "function_name": "tu_dai_nhat",
        "hint": "words = s.split(); max(words, key=len) — hoặc duyệt giữ từ dài nhất đầu tiên.",
        "starter_code": (
            "def tu_dai_nhat(s):\n"
            "    # Tra ve tu dai nhat (hoa thi lay tu xuat hien truoc)\n"
            "    pass\n\n"
            "# Thu: print(tu_dai_nhat(\"Em yeu lap trinh Python\"))\n"
        ),
        "testcases": [
            {
                "name": "Python dài nhất",
                "mode": "function",
                "function_name": "tu_dai_nhat",
                "args": ["Em yeu lap trinh Python"],
                "expected": "Python",
            },
            {
                "name": "Một từ",
                "mode": "function",
                "function_name": "tu_dai_nhat",
                "args": ["Code"],
                "expected": "Code",
            },
            {
                "name": "Hòa độ dài → lấy từ trước",
                "mode": "function",
                "function_name": "tu_dai_nhat",
                "args": ["cat dog bat"],
                "expected": "cat",
            },
            {
                "name": "Từ giữa dài hơn",
                "mode": "function",
                "function_name": "tu_dai_nhat",
                "args": ["a programming z"],
                "expected": "programming",
            },
        ],
        "order_num": 18,
    })

    # ── TL5: Tổng ước + số hoàn hảo ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 20 — TỔNG ƯỚC VÀ SỐ HOÀN HẢO\n\n"
            "Nhập số nguyên dương n.\n"
            "1) Tính tổng tất cả các ước dương của n (kể cả 1 và n).\n"
            "2) Kiểm tra n có phải số hoàn hảo hay không.\n\n"
            "Quy ước số hoàn hảo: tổng các ước dương của n "
            "không kể chính n bằng n. Ví dụ: 6 = 1+2+3.\n\n"
            "Viết hàm xu_ly_hoan_hao(n) trả về tuple "
            "(tong_uoc, la_hoan_hao) với la_hoan_hao là True/False.\n\n"
            "Ví dụ:\n"
            "xu_ly_hoan_hao(6) → (12, True)\n"
            "xu_ly_hoan_hao(10) → (18, False)"
        ),
        "points": 14,
        "allow_run": True,
        "function_name": "xu_ly_hoan_hao",
        "hint": (
            "tong = tổng mọi i từ 1..n mà n % i == 0. "
            "la_hoan_hao = (tong - n == n) tức tong == 2*n."
        ),
        "starter_code": (
            "def xu_ly_hoan_hao(n):\n"
            "    # Tra ve (tong_uoc, la_hoan_hao)\n"
            "    pass\n\n"
            "# Thu: print(xu_ly_hoan_hao(6))  # (12, True)\n"
        ),
        "testcases": [
            {
                "name": "n=6 hoàn hảo",
                "mode": "function",
                "function_name": "xu_ly_hoan_hao",
                "args": [6],
                "expected": [12, True],
            },
            {
                "name": "n=28 hoàn hảo",
                "mode": "function",
                "function_name": "xu_ly_hoan_hao",
                "args": [28],
                "expected": [56, True],
            },
            {
                "name": "n=10 không HH",
                "mode": "function",
                "function_name": "xu_ly_hoan_hao",
                "args": [10],
                "expected": [18, False],
            },
            {
                "name": "n=1",
                "mode": "function",
                "function_name": "xu_ly_hoan_hao",
                "args": [1],
                "expected": [1, False],
            },
            {
                "name": "n=12",
                "mode": "function",
                "function_name": "xu_ly_hoan_hao",
                "args": [12],
                "expected": [28, False],
            },
        ],
        "order_num": 19,
    })

    return questions


def main():
    app = create_app()
    with app.app_context():
        questions = sanitize_questions(build_questions())
        description = (
            "Bài kiểm tra Python 10/10 — 15 câu trắc nghiệm + 5 câu tự luận: "
            "Phân số tối giản · Viết hoa · Đếm từ · Từ dài nhất · Tổng ước & số hoàn hảo. "
            "Tự luận chấm bằng testcase (hàm)."
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
