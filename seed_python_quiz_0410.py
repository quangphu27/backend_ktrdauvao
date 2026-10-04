"""Seed: Bài kiểm tra Python 04/10 — 15 TN + 4 tự luận."""

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions

QUIZ_TITLE = "Bài kiểm tra Python ngày 04-10"
FIXED_SLUG = "python-0410"


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
            "Kết quả của biểu thức: 17 % 5",
            ["3", "2", "3.4", "0"],
            1,
            "B. 2 – 17 = 3×5 + 2.",
        ),
        mcq(
            3,
            "Số nào sau đây là số nguyên tố?",
            ["1", "9", "15", "13"],
            3,
            "D. 13 – Chỉ chia hết cho 1 và chính nó.",
        ),
        mcq(
            4,
            "Số nào sau đây là hợp số?",
            ["2", "3", "11", "12"],
            3,
            "D. 12 – Có ước thực sự ngoài 1 và chính nó.",
        ),
        mcq(
            5,
            "1 được xếp vào loại nào?",
            ["Số nguyên tố", "Hợp số", "Không phải nguyên tố cũng không phải hợp số", "Số chẵn"],
            2,
            "C. 1 không phải số nguyên tố và cũng không phải hợp số.",
        ),
        mcq(
            6,
            "Các ước dương của 12 là:",
            ["1, 2, 3, 4, 6, 12", "2, 3, 4, 6", "1, 12", "1, 2, 3, 12"],
            0,
            "A. 1, 2, 3, 4, 6, 12.",
        ),
        mcq(
            7,
            "Dãy nào tăng dần (mỗi số sau lớn hơn số trước)?",
            ["1, 3, 2, 5", "5, 4, 3, 2", "1, 2, 2, 3", "1, 2, 4, 7"],
            3,
            "D. 1 < 2 < 4 < 7.",
        ),
        mcq(
            8,
            "Trong dãy [2, 5, 2, 7, 2, 5], số xuất hiện nhiều lần nhất là:",
            ["5", "2", "7", "Không xác định"],
            1,
            "B. 2 xuất hiện 3 lần.",
        ),
        mcq(
            9,
            "Vòng lặp nào thường dùng để duyệt từng phần tử trong list?",
            ["if", "for", "class", "def"],
            1,
            "B. for – Đúng.",
        ),
        mcq(
            10,
            "Cách nào kiểm tra n chia hết cho d?",
            ["n / d == 0", "n // d == 0", "n % d == 0", "n ** d == 0"],
            2,
            "C. n % d == 0.",
        ),
        mcq(
            11,
            "Kết quả của đoạn mã?\n\nfor i in range(1, 4):\n    print(i, end=' ')",
            ["1 2 3", "1 2 3 4", "0 1 2 3", "1 2"],
            0,
            "A. range(1, 4) tạo 1, 2, 3.",
        ),
        mcq(
            12,
            "Hàm nào trả về số phần tử của list?",
            ["sum()", "max()", "len()", "count()"],
            2,
            "C. len() – Đúng.",
        ),
        mcq(
            13,
            "Để đếm số lần xuất hiện của x trong list ds, dùng:",
            ["ds.find(x)", "ds.count(x)", "len(x)", "ds.index(x)"],
            1,
            "B. ds.count(x).",
        ),
        mcq(
            14,
            "Điều kiện nào đúng để kiểm tra dãy ds có độ dài n tăng dần?",
            [
                "for i in range(n): nếu ds[i] > ds[i+1] thì không tăng",
                "for i in range(n-1): nếu ds[i] >= ds[i+1] thì không tăng",
                "chỉ cần ds[0] < ds[-1]",
                "chỉ cần max(ds) == ds[-1]",
            ],
            1,
            "B. Duyệt cặp liên tiếp; nếu có ds[i] >= ds[i+1] thì không tăng nghiêm ngặt.",
        ),
        mcq(
            15,
            "Khi tìm tất cả ước của n, vòng lặp thường chạy i từ:",
            ["1 đến n", "0 đến n", "2 đến n-1", "n đến 2n"],
            0,
            "A. i từ 1 đến n (hoặc tối ưu đến căn bậc hai).",
        ),
    ]

    # ── TL1: Đếm nguyên tố & hợp số ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 16 — ĐẾM SỐ NGUYÊN TỐ VÀ HỢP SỐ\n\n"
            "Nhập n và n số nguyên.\n"
            "Kiểm tra trong n số đó có bao nhiêu số nguyên tố, bao nhiêu hợp số.\n\n"
            "Quy ước:\n"
            "- Số nguyên tố: số nguyên > 1, chỉ có ước 1 và chính nó.\n"
            "- Hợp số: số nguyên > 1 và không phải số nguyên tố.\n"
            "- Số 1 (và số ≤ 1) không tính vào nguyên tố cũng không tính vào hợp số.\n\n"
            "Viết hàm dem_nt_hs(ds) nhận list số nguyên, "
            "trả về tuple (so_nguyen_to, so_hop_so).\n\n"
            "Ví dụ: dem_nt_hs([1, 2, 3, 4, 9]) → (2, 2)\n"
            "(Nguyên tố: 2, 3 · Hợp số: 4, 9 · 1 bỏ qua)"
        ),
        "points": 18,
        "allow_run": True,
        "function_name": "dem_nt_hs",
        "hint": (
            "Viết hàm is_prime(x). Với mỗi số trong ds: "
            "nếu > 1 và is_prime thì đếm NT; nếu > 1 và không prime thì đếm HS."
        ),
        "starter_code": (
            "def is_prime(x):\n"
            "    if x <= 1:\n"
            "        return False\n"
            "    for i in range(2, int(x**0.5) + 1):\n"
            "        if x % i == 0:\n"
            "            return False\n"
            "    return True\n\n"
            "def dem_nt_hs(ds):\n"
            "    # Tra ve (so_nguyen_to, so_hop_so)\n"
            "    pass\n\n"
            "# Thu: print(dem_nt_hs([1, 2, 3, 4, 9]))  # (2, 2)\n"
        ),
        "testcases": [
            {
                "name": "1,2,3,4,9 → (2,2)",
                "mode": "function",
                "function_name": "dem_nt_hs",
                "args": [[1, 2, 3, 4, 9]],
                "expected": [2, 2],
            },
            {
                "name": "Toàn nguyên tố",
                "mode": "function",
                "function_name": "dem_nt_hs",
                "args": [[2, 3, 5, 7]],
                "expected": [4, 0],
            },
            {
                "name": "Toàn hợp số",
                "mode": "function",
                "function_name": "dem_nt_hs",
                "args": [[4, 6, 8, 9]],
                "expected": [0, 4],
            },
            {
                "name": "Có số âm và 1",
                "mode": "function",
                "function_name": "dem_nt_hs",
                "args": [[-3, 0, 1, 11, 15]],
                "expected": [1, 1],
            },
        ],
        "order_num": 15,
    })

    # ── TL2: Ước của n ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 17 — CÁC ƯỚC CỦA N\n\n"
            "Nhập n. In ra tất cả các ước dương của n.\n\n"
            "Viết hàm liet_ke_uoc(n) trả về list các ước dương của n "
            "theo thứ tự tăng dần.\n\n"
            "Ví dụ: liet_ke_uoc(12) → [1, 2, 3, 4, 6, 12]"
        ),
        "points": 17,
        "allow_run": True,
        "function_name": "liet_ke_uoc",
        "hint": "for i in range(1, n+1): if n % i == 0: thêm i vào list",
        "starter_code": (
            "def liet_ke_uoc(n):\n"
            "    # Tra ve list cac uoc duong cua n (tang dan)\n"
            "    pass\n\n"
            "# Thu: print(liet_ke_uoc(12))  # [1, 2, 3, 4, 6, 12]\n"
        ),
        "testcases": [
            {
                "name": "n=12",
                "mode": "function",
                "function_name": "liet_ke_uoc",
                "args": [12],
                "expected": [1, 2, 3, 4, 6, 12],
            },
            {
                "name": "n=7 (nguyên tố)",
                "mode": "function",
                "function_name": "liet_ke_uoc",
                "args": [7],
                "expected": [1, 7],
            },
            {
                "name": "n=1",
                "mode": "function",
                "function_name": "liet_ke_uoc",
                "args": [1],
                "expected": [1],
            },
            {
                "name": "n=100",
                "mode": "function",
                "function_name": "liet_ke_uoc",
                "args": [100],
                "expected": [1, 2, 4, 5, 10, 20, 25, 50, 100],
            },
        ],
        "order_num": 16,
    })

    # ── TL3: Dãy tăng dần ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 18 — DÃY SỐ TĂNG\n\n"
            "Nhập n số nguyên.\n"
            "Hãy kiểm tra xem dãy số vừa nhập có tăng dần hay không.\n\n"
            "Quy ước tăng dần: mỗi phần tử sau phải lớn hơn phần tử trước "
            "(ds[i] < ds[i+1] với mọi i).\n\n"
            "Viết hàm kiem_tra_tang(ds) trả về True nếu dãy tăng dần, "
            "ngược lại False.\n\n"
            "Ví dụ:\n"
            "kiem_tra_tang([1, 2, 4, 7]) → True\n"
            "kiem_tra_tang([1, 2, 2, 3]) → False"
        ),
        "points": 17,
        "allow_run": True,
        "function_name": "kiem_tra_tang",
        "hint": "for i in range(len(ds)-1): if ds[i] >= ds[i+1]: return False",
        "starter_code": (
            "def kiem_tra_tang(ds):\n"
            "    # Tra ve True neu day tang dan, nguoc lai False\n"
            "    pass\n\n"
            "# Thu: print(kiem_tra_tang([1, 2, 4, 7]))  # True\n"
        ),
        "testcases": [
            {
                "name": "Tăng dần",
                "mode": "function",
                "function_name": "kiem_tra_tang",
                "args": [[1, 2, 4, 7]],
                "expected": True,
            },
            {
                "name": "Có phần tử bằng nhau",
                "mode": "function",
                "function_name": "kiem_tra_tang",
                "args": [[1, 2, 2, 3]],
                "expected": False,
            },
            {
                "name": "Giảm",
                "mode": "function",
                "function_name": "kiem_tra_tang",
                "args": [[5, 4, 3]],
                "expected": False,
            },
            {
                "name": "Một phần tử",
                "mode": "function",
                "function_name": "kiem_tra_tang",
                "args": [[10]],
                "expected": True,
            },
            {
                "name": "Hai phần tử tăng",
                "mode": "function",
                "function_name": "kiem_tra_tang",
                "args": [[-1, 0]],
                "expected": True,
            },
        ],
        "order_num": 17,
    })

    # ── TL4: Số xuất hiện nhiều nhất ──
    questions.append({
        "type": "python_code",
        "content": (
            "Câu 19 — SỐ XUẤT HIỆN NHIỀU LẦN NHẤT\n\n"
            "Nhập dãy N số nguyên.\n"
            "Hãy tìm số xuất hiện nhiều lần nhất.\n\n"
            "Nếu có nhiều số cùng số lần xuất hiện lớn nhất, "
            "trả về số nhỏ nhất trong các số đó.\n\n"
            "Viết hàm xuat_hien_nhieu_nhat(ds) trả về số đó.\n\n"
            "Ví dụ:\n"
            "xuat_hien_nhieu_nhat([2, 5, 2, 7, 2, 5]) → 2\n"
            "xuat_hien_nhieu_nhat([1, 3, 1, 3]) → 1"
        ),
        "points": 18,
        "allow_run": True,
        "function_name": "xuat_hien_nhieu_nhat",
        "hint": (
            "Dùng count hoặc dict đếm. "
            "Chọn số có count lớn nhất; nếu hòa thì lấy số nhỏ hơn."
        ),
        "starter_code": (
            "def xuat_hien_nhieu_nhat(ds):\n"
            "    # Tra ve so xuat hien nhieu lan nhat (hoa thi lay so nho hon)\n"
            "    pass\n\n"
            "# Thu: print(xuat_hien_nhieu_nhat([2, 5, 2, 7, 2, 5]))  # 2\n"
        ),
        "testcases": [
            {
                "name": "2 xuất hiện 3 lần",
                "mode": "function",
                "function_name": "xuat_hien_nhieu_nhat",
                "args": [[2, 5, 2, 7, 2, 5]],
                "expected": 2,
            },
            {
                "name": "Hòa → lấy số nhỏ hơn",
                "mode": "function",
                "function_name": "xuat_hien_nhieu_nhat",
                "args": [[1, 3, 1, 3]],
                "expected": 1,
            },
            {
                "name": "Một phần tử",
                "mode": "function",
                "function_name": "xuat_hien_nhieu_nhat",
                "args": [[9]],
                "expected": 9,
            },
            {
                "name": "Tất cả khác nhau → số nhỏ nhất",
                "mode": "function",
                "function_name": "xuat_hien_nhieu_nhat",
                "args": [[4, 1, 3]],
                "expected": 1,
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
            "Bài kiểm tra Python 04/10 — 15 câu trắc nghiệm + 4 câu tự luận: "
            "Đếm nguyên tố/hợp số · Liệt kê ước · Dãy tăng · Số xuất hiện nhiều nhất. "
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
