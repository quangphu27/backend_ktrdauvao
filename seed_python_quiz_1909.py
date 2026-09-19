"""Seed: Bài kiểm tra Python 19/09 — 15 TN + 4 tự luận."""

import random
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions

QUIZ_TITLE = "Bài kiểm tra Python ngày 19-09"
FIXED_SLUG = "python-1909"


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
        "Cách nào lấy value theo key trong dictionary d?",
        ["d.get(key)", "d.add(key)", "d.push(key)", "d.append(key)"],
        0,
        "A. d.get(key) – (hoặc d[key]).",
    ),
    mcq(
        "Kết quả của chương trình?\n\nd = {'a': 1, 'b': 2}\nprint(d['b'])",
        ["1", "2", "b", "Error"],
        1,
        "B. 2 – Lấy value của key 'b'.",
    ),
    mcq(
        "Chuỗi đảo của 'python' là gì?\n\ns = 'python'\nprint(s[::-1])",
        ["python", "nohtyp", "PYTHON", "Error"],
        1,
        "B. nohtyp – Cắt ngược chuỗi.",
    ),
    mcq(
        "Cách nào kiểm tra hai chuỗi giống nhau khi đọc ngược?",
        ["s == s[::-1]", "s == reverse(s)", "s.reverse()", "len(s) % 2 == 0"],
        0,
        "A. s == s[::-1] – Điều kiện chuỗi đối xứng.",
    ),
    mcq(
        "Kết quả của biểu thức: 10 // 3",
        ["3.33", "3", "1", "30"],
        1,
        "B. 3 – // là chia lấy phần nguyên.",
    ),
    mcq(
        "Hàm nào trong module math tìm ước chung lớn nhất?",
        ["math.gcd", "math.lcm", "math.max", "math.div"],
        0,
        "A. math.gcd – Greatest Common Divisor.",
    ),
    mcq(
        "Phân số a/b tối giản khi nào?",
        ["a > b", "UCLN(a, b) = 1", "a chia hết b", "b = 0"],
        1,
        "B. UCLN(a, b) = 1 – Không còn ước chung > 1.",
    ),
    mcq(
        "Hoán vị a, b đúng cách nào?",
        ["a = b; b = a", "a, b = b, a", "swap(a, b)", "a + b = b + a"],
        1,
        "B. a, b = b, a – Hoán vị đồng thời trong Python.",
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
        "Lệnh nào dùng để nhập dữ liệu từ bàn phím?",
        ["get()", "scan()", "input()", "read()"],
        2,
        "C. input() – Đúng.",
    ),
    mcq(
        "Kết quả của lệnh: print(type(3.14))",
        ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'bool'>"],
        1,
        "B. float – Đúng.",
    ),
    mcq(
        "Kết quả của biểu thức: len('madam')",
        ["4", "5", "6", "Error"],
        1,
        "B. 5 – Chuỗi có 5 ký tự.",
    ),
    mcq(
        "Đâu là cách gán giá trị đúng cho biến x?",
        ["x == 5", "x := 5", "x = 5", "5 = x"],
        2,
        "C. x = 5 – Phép gán dùng một dấu =.",
    ),
]


def build_questions():
    rng = random.Random(1909)
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

    # ── TL1: Từ điển Anh – Việt ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 16 — TỪ ĐIỂN ANH – VIỆT\n\n"
            "Tạo chương trình Từ điển Anh – Việt lưu dưới dạng dict "
            "(key = tiếng Anh, value = tiếng Việt). Chương trình cho phép:\n"
            "1. Nhập từ mới\n"
            "2. Tìm kiếm từ\n"
            "3. In từ điển\n"
            "4. Thoát\n\n"
            "Yêu cầu viết đúng 3 hàm (hệ thống gọi để chấm):\n"
            "- them_tu(tudien, tu_anh, nghia): thêm cặp từ, return nghia vừa thêm.\n"
            "- tim_kiem(tudien, tu_anh): trả về nghĩa nếu có; "
            "không có thì return đúng chuỗi: Khong tim thay\n"
            "- in_tudien(tudien): trả về chuỗi các cặp \"tu: nghia\" "
            "cách nhau bằng \"; \" (theo thứ tự key tăng dần). "
            "Ví dụ: book: sach; hello: xin chao"
        ),
        "points": 5,
        "allow_run": True,
        "hint": (
            "them_tu: tudien[tu_anh]=nghia; return nghia. "
            "tim_kiem: return tudien.get(tu_anh, 'Khong tim thay'). "
            "in_tudien: '; '.join(f'{k}: {tudien[k]}' for k in sorted(tudien))"
        ),
        "starter_code": (
            "def them_tu(tudien, tu_anh, nghia):\n"
            "    # Them tu moi, return nghia vua them\n"
            "    pass\n\n"
            "def tim_kiem(tudien, tu_anh):\n"
            "    # Tra ve nghia hoac 'Khong tim thay'\n"
            "    pass\n\n"
            "def in_tudien(tudien):\n"
            "    # Tra ve chuoi 'key: value; key2: value2' (sorted key)\n"
            "    pass\n\n"
            "# Thu:\n"
            "# d = {}\n"
            "# print(them_tu(d, 'hello', 'xin chao'))\n"
            "# print(tim_kiem(d, 'hello'))\n"
            "# print(in_tudien(d))\n"
        ),
        "testcases": [
            {
                "name": "Thêm từ hello",
                "mode": "function",
                "function_name": "them_tu",
                "args": [{}, "hello", "xin chao"],
                "expected": "xin chao",
            },
            {
                "name": "Thêm từ book",
                "mode": "function",
                "function_name": "them_tu",
                "args": [{"hello": "xin chao"}, "book", "sach"],
                "expected": "sach",
            },
            {
                "name": "Tìm thấy — hello",
                "mode": "function",
                "function_name": "tim_kiem",
                "args": [{"hello": "xin chao", "book": "sach"}, "hello"],
                "expected": "xin chao",
            },
            {
                "name": "Không tìm thấy",
                "mode": "function",
                "function_name": "tim_kiem",
                "args": [{"hello": "xin chao"}, "bye"],
                "expected": "Khong tim thay",
            },
            {
                "name": "In từ điển (sorted)",
                "mode": "function",
                "function_name": "in_tudien",
                "args": [{"hello": "xin chao", "book": "sach"}],
                "expected": "book: sach; hello: xin chao",
            },
        ],
        "order_num": 15,
    })

    # ── TL2: Hoán vị 2 số ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 17 — HOÁN VỊ 2 SỐ\n\n"
            "Viết chương trình hoán vị 2 số a, b nhập từ bàn phím. "
            "Hoán vị rồi in kết quả ra màn hình.\n\n"
            "Ví dụ: a=5, b=3 → Kết quả a=3, b=5\n\n"
            "Viết hàm hoan_vi(a, b) trả về chuỗi đúng dạng: a=3, b=5 "
            "(sau khi đã hoán vị).\n"
            "Hệ thống gọi hàm để chấm."
        ),
        "points": 5,
        "allow_run": True,
        "function_name": "hoan_vi",
        "hint": "a, b = b, a; return f'a={a}, b={b}'",
        "starter_code": (
            "def hoan_vi(a, b):\n"
            "    # Hoan vi roi return chuoi: 'a=..., b=...'\n"
            "    pass\n\n"
            "# Thu: print(hoan_vi(5, 3))  # a=3, b=5\n"
        ),
        "testcases": [
            {
                "name": "a=5, b=3",
                "mode": "function",
                "function_name": "hoan_vi",
                "args": [5, 3],
                "expected": "a=3, b=5",
            },
            {
                "name": "a=1, b=9",
                "mode": "function",
                "function_name": "hoan_vi",
                "args": [1, 9],
                "expected": "a=9, b=1",
            },
            {
                "name": "a=0, b=7",
                "mode": "function",
                "function_name": "hoan_vi",
                "args": [0, 7],
                "expected": "a=7, b=0",
            },
            {
                "name": "a=-2, b=4",
                "mode": "function",
                "function_name": "hoan_vi",
                "args": [-2, 4],
                "expected": "a=4, b=-2",
            },
        ],
        "order_num": 16,
    })

    # ── TL3: Phân số ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 18 — PHÂN SỐ a/b\n\n"
            "Viết chương trình nhận phân số dạng a/b:\n"
            "1. Kiểm tra xem có phải phân số tối giản hay không\n"
            "2. Rút gọn phân số hoặc đưa về dạng hỗn số\n\n"
            "Yêu cầu viết đúng 2 hàm:\n"
            "- la_toi_gian(a, b): return True nếu UCLN(|a|,|b|)=1, ngược lại False. "
            "(Giả sử b ≠ 0)\n"
            "- rut_gon(a, b): rút gọn a/b; nếu |a| ≥ |b| thì trả về hỗn số "
            "dạng \"q r/m\" (thương q, dư r, mẫu m sau rút gọn); "
            "nếu |a| < |b| thì trả về \"r/m\". "
            "Ví dụ: rut_gon(8, 12) → \"2/3\"; rut_gon(10, 4) → \"2 1/2\"; "
            "rut_gon(3, 5) → \"3/5\".\n"
            "(Với a, b dương trong các testcase.)"
        ),
        "points": 5,
        "allow_run": True,
        "hint": (
            "import math; g=math.gcd(a,b); "
            "la_toi_gian: return g==1. "
            "rut_gon: a//=g; b//=g; "
            "neu a>=b: return f'{a//b} {a%b}/{b}' (neu a%b!=0) "
            "hoac f'{a//b}' (neu a%b==0); else return f'{a}/{b}'"
        ),
        "starter_code": (
            "import math\n\n"
            "def la_toi_gian(a, b):\n"
            "    # True neu UCLN(a,b)==1\n"
            "    pass\n\n"
            "def rut_gon(a, b):\n"
            "    # Rut gon; neu a>=b thi dang hon so 'q r/m' (hoac 'q' neu du=0)\n"
            "    # neu a<b thi 'r/m'\n"
            "    pass\n\n"
            "# Thu: print(la_toi_gian(3, 5))   # True\n"
            "# Thu: print(rut_gon(8, 12))      # 2/3\n"
            "# Thu: print(rut_gon(10, 4))      # 2 1/2\n"
        ),
        "testcases": [
            {
                "name": "3/5 tối giản",
                "mode": "function",
                "function_name": "la_toi_gian",
                "args": [3, 5],
                "expected": True,
            },
            {
                "name": "8/12 chưa tối giản",
                "mode": "function",
                "function_name": "la_toi_gian",
                "args": [8, 12],
                "expected": False,
            },
            {
                "name": "Rút gọn 8/12 → 2/3",
                "mode": "function",
                "function_name": "rut_gon",
                "args": [8, 12],
                "expected": "2/3",
            },
            {
                "name": "Hỗn số 10/4 → 2 1/2",
                "mode": "function",
                "function_name": "rut_gon",
                "args": [10, 4],
                "expected": "2 1/2",
            },
            {
                "name": "3/5 giữ nguyên",
                "mode": "function",
                "function_name": "rut_gon",
                "args": [3, 5],
                "expected": "3/5",
            },
            {
                "name": "Hỗn số nguyên 9/3 → 3",
                "mode": "function",
                "function_name": "rut_gon",
                "args": [9, 3],
                "expected": "3",
            },
        ],
        "order_num": 17,
    })

    # ── TL4: Chuỗi đối xứng ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 19 — CHUỖI ĐỐI XỨNG\n\n"
            "Nhập vào một chuỗi s và kiểm tra xem chuỗi đó có phải chuỗi đối xứng hay không.\n"
            "Một chuỗi được gọi là đối xứng nếu đọc từ trái sang phải giống "
            "đọc từ phải sang trái.\n"
            "Ví dụ: madam, level là các chuỗi đối xứng.\n\n"
            "Viết hàm la_doi_xung(s) trả về True nếu đối xứng, False nếu không.\n"
            "(Không phân biệt khoảng trắng thừa — so sánh đúng chuỗi s đã cho.)"
        ),
        "points": 5,
        "allow_run": True,
        "function_name": "la_doi_xung",
        "hint": "return s == s[::-1]",
        "starter_code": (
            "def la_doi_xung(s):\n"
            "    # True neu s doc xuoi = doc nguoc\n"
            "    pass\n\n"
            "# Thu: print(la_doi_xung('madam'))  # True\n"
            "# Thu: print(la_doi_xung('python')) # False\n"
        ),
        "testcases": [
            {
                "name": "madam",
                "mode": "function",
                "function_name": "la_doi_xung",
                "args": ["madam"],
                "expected": True,
            },
            {
                "name": "level",
                "mode": "function",
                "function_name": "la_doi_xung",
                "args": ["level"],
                "expected": True,
            },
            {
                "name": "python",
                "mode": "function",
                "function_name": "la_doi_xung",
                "args": ["python"],
                "expected": False,
            },
            {
                "name": "aba",
                "mode": "function",
                "function_name": "la_doi_xung",
                "args": ["aba"],
                "expected": True,
            },
            {
                "name": "ab",
                "mode": "function",
                "function_name": "la_doi_xung",
                "args": ["ab"],
                "expected": False,
            },
            {
                "name": "Một ký tự",
                "mode": "function",
                "function_name": "la_doi_xung",
                "args": ["a"],
                "expected": True,
            },
        ],
        "order_num": 18,
    })

    return questions


def main():
    app = create_app()
    with app.app_context():
        questions = sanitize_questions(build_questions())
        description = (
            "Bài kiểm tra Python 19/09 — 15 câu trắc nghiệm + 4 câu tự luận: "
            "Từ điển Anh–Việt · Hoán vị 2 số · Phân số · Chuỗi đối xứng. "
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
