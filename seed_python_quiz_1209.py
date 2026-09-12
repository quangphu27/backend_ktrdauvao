"""Seed: Bài kiểm tra Python 12/09 — 20 TN (đảo thứ tự) + 3 tự luận code."""

import random
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions

QUIZ_TITLE = "Bài kiểm tra Python ngày 12-09"
FIXED_SLUG = "python-1209"

# Kết quả chuẩn câu 1 (2000–3200, %7==0 và %5!=0)
DIV7_NOT5 = (
    "2002,2009,2016,2023,2037,2044,2051,2058,2072,2079,2086,2093,2107,2114,2121,2128,"
    "2142,2149,2156,2163,2177,2184,2191,2198,2212,2219,2226,2233,2247,2254,2261,2268,"
    "2282,2289,2296,2303,2317,2324,2331,2338,2352,2359,2366,2373,2387,2394,2401,2408,"
    "2422,2429,2436,2443,2457,2464,2471,2478,2492,2499,2506,2513,2527,2534,2541,2548,"
    "2562,2569,2576,2583,2597,2604,2611,2618,2632,2639,2646,2653,2667,2674,2681,2688,"
    "2702,2709,2716,2723,2737,2744,2751,2758,2772,2779,2786,2793,2807,2814,2821,2828,"
    "2842,2849,2856,2863,2877,2884,2891,2898,2912,2919,2926,2933,2947,2954,2961,2968,"
    "2982,2989,2996,3003,3017,3024,3031,3038,3052,3059,3066,3073,3087,3094,3101,3108,"
    "3122,3129,3136,3143,3157,3164,3171,3178,3192,3199"
)


def mcq(content, options, correct_idx, explanation):
    opts = [{"text": t, "is_correct": i == correct_idx} for i, t in enumerate(options)]
    return {
        "type": "mcq",
        "content": content,
        "points": 1,
        "options": opts,
        "explanation": explanation.strip(),
    }


# Ngân hàng lý thuyết từ các bài trước — lấy 20 câu rồi xáo
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
        "Tên biến nào sau đây hợp lệ trong Python?",
        ["ho ten", "ho-ten", "ho_ten", "ho@ten"],
        2,
        "C. ho_ten – Đúng.",
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
    mcq(
        "Kết quả của lệnh: print(type(3.14))",
        ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'bool'>"],
        1,
        "B. float – Đúng.",
    ),
    mcq(
        "Cú pháp nào đúng để tạo dictionary rỗng?",
        ["d = []", "d = ()", "d = {}", "d = <>"],
        2,
        "C. d = {} – Đúng.",
    ),
]


def build_questions():
    rng = random.Random(1209)
    picked = rng.sample(MCQ_BANK, 20)
    questions = []
    for i, q in enumerate(picked):
        item = dict(q)
        item["content"] = f"Câu {i + 1}: {q['content']}"
        item["order_num"] = i
        opts = list(item["options"])
        rng.shuffle(opts)
        item["options"] = opts
        questions.append(item)

    # ── Tự luận 1: số chia hết 7 không phải bội 5 ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 21 — Số chia hết cho 7 nhưng không phải bội của 5\n\n"
            "Viết chương trình tìm tất cả các số chia hết cho 7 nhưng không phải bội số của 5, "
            "nằm trong đoạn 2000 và 3200 (tính cả 2000 và 3200). "
            "Các số thu được sẽ được in thành chuỗi trên một dòng, cách nhau bằng dấu phẩy.\n\n"
            "Gợi ý:\n"
            "j = []  # Tạo một danh sách rỗng để lưu kết quả\n"
            "print(','.join(j))"
        ),
        "points": 5,
        "allow_run": True,
        "hint": (
            "for i in range(2000, 3201): "
            "if i % 7 == 0 and i % 5 != 0: j.append(str(i))"
        ),
        "starter_code": (
            "j = []  # Tao danh sach rong de luu ket qua\n\n"
            "# Duyet tu 2000 den 3200 (tinh ca 2 dau)\n"
            "# Neu chia het cho 7 va khong chia het cho 5 thi them vao j\n\n"
            "print(','.join(j))\n"
        ),
        "testcases": [
            {
                "name": "In đúng chuỗi số",
                "mode": "stdin",
                "stdin": "",
                "expected_stdout": DIV7_NOT5,
            },
            {
                "name": "Bắt đầu bằng 2002",
                "mode": "stdin",
                "stdin": "",
                "expected_stdout": DIV7_NOT5,
            },
        ],
        "order_num": 20,
    })

    # ── Tự luận 2: giai thừa ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 22 — Tính giai thừa\n\n"
            "Viết một chương trình có thể tính giai thừa của một số cho trước.\n"
            "Chương trình nhập một số nguyên n từ bàn phím và in ra n!.\n\n"
            "Ví dụ: 5! = 120\n\n"
            "Gợi ý: dùng vòng lặp for hoặc while; quy ước 0! = 1."
        ),
        "points": 5,
        "allow_run": True,
        "hint": "n = int(input()); gt = 1; for i in range(1, n+1): gt *= i; print(gt)",
        "starter_code": (
            'n = int(input("Nhap n: "))\n'
            "gt = 1\n\n"
            "# Tinh n! roi in ket qua\n"
        ),
        "testcases": [
            {"name": "5! = 120", "mode": "stdin", "stdin": "5\n", "expected_stdout": "120"},
            {"name": "0! = 1", "mode": "stdin", "stdin": "0\n", "expected_stdout": "1"},
            {"name": "1! = 1", "mode": "stdin", "stdin": "1\n", "expected_stdout": "1"},
            {"name": "6! = 720", "mode": "stdin", "stdin": "6\n", "expected_stdout": "720"},
            {"name": "10! = 3628800", "mode": "stdin", "stdin": "10\n", "expected_stdout": "3628800"},
        ],
        "order_num": 21,
    })

    # ── Tự luận 3: Từ điển tiếng Anh ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 23 — Từ điển tiếng Anh\n\n"
            "Viết chương trình từ điển tiếng Anh với 2 chức năng:\n"
            "1. Thêm từ mới\n"
            "2. Tìm kiếm\n\n"
            "Gợi ý: sử dụng Dictionary.\n\n"
            "Yêu cầu viết đúng 2 hàm (hệ thống sẽ gọi để chấm):\n"
            "- them_tu(tudien, tu_anh, nghia): thêm cặp từ vào dictionary "
            "(tu_anh là key, nghia là value), rồi return nghia vừa thêm.\n"
            "- tim_kiem(tudien, tu_anh): trả về nghĩa nếu tìm thấy; "
            "nếu không có thì return đúng chuỗi: Khong tim thay"
        ),
        "points": 5,
        "allow_run": True,
        "hint": (
            "them_tu: tudien[tu_anh] = nghia; return nghia. "
            "tim_kiem: return tudien.get(tu_anh, 'Khong tim thay')"
        ),
        "starter_code": (
            "def them_tu(tudien, tu_anh, nghia):\n"
            "    # Them tu moi, return nghia vua them\n"
            "    pass\n\n"
            "def tim_kiem(tudien, tu_anh):\n"
            "    # Tra ve nghia hoac 'Khong tim thay'\n"
            "    pass\n\n"
            "# Thu nghiem:\n"
            "# d = {}\n"
            "# print(them_tu(d, 'hello', 'xin chao'))\n"
            "# print(tim_kiem(d, 'hello'))\n"
            "# print(tim_kiem(d, 'bye'))\n"
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
                "name": "Tìm thấy — book",
                "mode": "function",
                "function_name": "tim_kiem",
                "args": [{"hello": "xin chao", "book": "sach"}, "book"],
                "expected": "sach",
            },
            {
                "name": "Không tìm thấy",
                "mode": "function",
                "function_name": "tim_kiem",
                "args": [{"hello": "xin chao"}, "bye"],
                "expected": "Khong tim thay",
            },
        ],
        "order_num": 22,
    })

    return questions


def main():
    app = create_app()
    with app.app_context():
        questions = sanitize_questions(build_questions())
        description = (
            "Bài kiểm tra Python 12/09 — 20 câu trắc nghiệm lý thuyết (đảo thứ tự) "
            "+ 3 câu tự luận: Số chia hết 7 · Giai thừa · Từ điển tiếng Anh. "
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
