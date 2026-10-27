"""Seed: Bài kiểm tra Python 25/10 — 5 câu tự luận."""

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions

QUIZ_TITLE = "Bài kiểm tra Python ngày 25-10"
FIXED_SLUG = "python-2510"


def build_questions():
    questions = []

    questions.append({
        "type": "python_code",
        "content": (
            "Câu 1 — CỬA HÀNG BÁN NƯỚC\n\n"
            "Một cửa hàng bán nước lọc giá 5.000 đồng và nước cam giá 10.000 đồng.\n"
            "Viết chương trình cho người dùng chọn loại nước và nhập số tiền đã trả. "
            "Thông báo số tiền thừa hoặc còn thiếu.\n\n"
            "Yêu cầu chấm tự động — viết hàm:\n"
            "tinh_tien(loai, tien_tra)\n"
            "- loai = 1 → nước lọc (5.000đ)\n"
            "- loai = 2 → nước cam (10.000đ)\n"
            "- Trả về: tiền thừa (số dương), còn thiếu (số âm), hoặc 0 nếu vừa đủ.\n\n"
            "Ví dụ:\n"
            "tinh_tien(1, 8000) → 3000     (thừa 3.000)\n"
            "tinh_tien(1, 2000) → -3000    (thiếu 3.000)\n"
            "tinh_tien(2, 10000) → 0       (vừa đủ)\n"
            "tinh_tien(2, 15000) → 5000"
        ),
        "points": 20,
        "allow_run": True,
        "function_name": "tinh_tien",
        "hint": (
            "gia = 5000 if loai == 1 else 10000; return tien_tra - gia. "
            "Menu: print 1/2, loai = int(input()), tien = int(input()), "
            "rồi in Thua / Thieu / Du."
        ),
        "starter_code": (
            "def tinh_tien(loai, tien_tra):\n"
            "    # loai 1 = nuoc loc 5000, loai 2 = nuoc cam 10000\n"
            "    # Tra ve tien_tra - gia  (duong = thua, am = thieu, 0 = du)\n"
            "    pass\n\n"
            "# ===== MENU (viet them) =====\n"
            '# print("1. Nuoc loc - 5000 dong")\n'
            '# print("2. Nuoc cam - 10000 dong")\n'
            '# loai = int(input("Chon loai nuoc: "))\n'
            '# tien = int(input("So tien da tra: "))\n'
            "# kq = tinh_tien(loai, tien)\n"
            "# if kq > 0:\n"
            '#     print("Thua", kq)\n'
            "# elif kq < 0:\n"
            '#     print("Thieu", -kq)\n'
            "# else:\n"
            '#     print("Du")\n'
        ),
        "testcases": [
            {"name": "Lọc thừa 8000-5000", "mode": "function", "function_name": "tinh_tien", "args": [1, 8000], "expected": 3000},
            {"name": "Lọc thiếu 2000-5000", "mode": "function", "function_name": "tinh_tien", "args": [1, 2000], "expected": -3000},
            {"name": "Lọc vừa 5000", "mode": "function", "function_name": "tinh_tien", "args": [1, 5000], "expected": 0},
            {"name": "Cam thừa 15000", "mode": "function", "function_name": "tinh_tien", "args": [2, 15000], "expected": 5000},
            {"name": "Cam thiếu 7000", "mode": "function", "function_name": "tinh_tien", "args": [2, 7000], "expected": -3000},
            {"name": "Cam vừa 10000", "mode": "function", "function_name": "tinh_tien", "args": [2, 10000], "expected": 0},
        ],
        "order_num": 0,
    })

    questions.append({
        "type": "python_code",
        "content": (
            "Câu 2 — CÁC SỐ CHẴN TỪ 1 ĐẾN N\n\n"
            "Viết chương trình nhập số nguyên dương n. "
            "In ra tất cả các số chẵn từ 1 đến n.\n\n"
            "Ví dụ: Nhập n = 12 → 2 4 6 8 10 12\n\n"
            "Yêu cầu chấm tự động — viết hàm so_chan(n) "
            "trả về list các số chẵn từ 1 đến n (tăng dần).\n\n"
            "Ví dụ:\n"
            "so_chan(12) → [2, 4, 6, 8, 10, 12]\n"
            "so_chan(7) → [2, 4, 6]\n"
            "so_chan(1) → []"
        ),
        "points": 20,
        "allow_run": True,
        "function_name": "so_chan",
        "hint": "ket_qua = []; for i in range(1, n+1): if i % 2 == 0: ket_qua.append(i); return ket_qua. Hoặc list(range(2, n+1, 2)).",
        "starter_code": (
            "def so_chan(n):\n"
            "    # Tra ve list cac so chan tu 1 den n\n"
            "    pass\n\n"
            "# Thu: print(so_chan(12))  # [2, 4, 6, 8, 10, 12]\n"
            '# n = int(input("Nhap n: "))\n'
            "# print(*so_chan(n))\n"
        ),
        "testcases": [
            {"name": "n=12", "mode": "function", "function_name": "so_chan", "args": [12], "expected": [2, 4, 6, 8, 10, 12]},
            {"name": "n=7", "mode": "function", "function_name": "so_chan", "args": [7], "expected": [2, 4, 6]},
            {"name": "n=1 → rỗng", "mode": "function", "function_name": "so_chan", "args": [1], "expected": []},
            {"name": "n=2", "mode": "function", "function_name": "so_chan", "args": [2], "expected": [2]},
            {"name": "n=20", "mode": "function", "function_name": "so_chan", "args": [20], "expected": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]},
        ],
        "order_num": 1,
    })

    questions.append({
        "type": "python_code",
        "content": (
            "Câu 3 — MẬT MÃ CHIẾC KÉT\n\n"
            "Một chiếc két có mật mã gồm ba chữ số khác nhau. "
            "Mật mã thỏa mãn các điều kiện:\n"
            "- Tổng ba chữ số bằng 15.\n"
            "- Chữ số hàng trăm lớn hơn chữ số hàng chục.\n"
            "- Mật mã chia hết cho 5.\n\n"
            "Yêu cầu chấm tự động — viết 2 hàm:\n"
            "- la_mat_ma(n) → True/False nếu n (số có 3 chữ số) thỏa mãn.\n"
            "- tim_mat_ma() → list tất cả mật mã, sắp xếp tăng dần.\n\n"
            "Ví dụ:\n"
            "la_mat_ma(645) → True\n"
            "la_mat_ma(123) → False\n"
            "tim_mat_ma() → [645, 735, 825, 870, 915, 960]"
        ),
        "points": 20,
        "allow_run": True,
        "function_name": "tim_mat_ma",
        "hint": (
            "for n in range(100, 1000): "
            "a,b,c = n//100, (n//10)%10, n%10; "
            "if len({a,b,c})==3 and a+b+c==15 and a>b and n%5==0."
        ),
        "starter_code": (
            "def la_mat_ma(n):\n"
            "    # True neu n gom 3 chu so KHAC NHAU, tong = 15,\n"
            "    # hang tram > hang chuc, va n chia het cho 5\n"
            "    pass\n\n"
            "def tim_mat_ma():\n"
            "    # Tra ve list tat ca mat ma, sap xep tang dan\n"
            "    pass\n\n"
            "# Thu: print(tim_mat_ma())\n"
        ),
        "testcases": [
            {"name": "645 đúng", "mode": "function", "function_name": "la_mat_ma", "args": [645], "expected": True},
            {"name": "960 đúng", "mode": "function", "function_name": "la_mat_ma", "args": [960], "expected": True},
            {"name": "123 sai", "mode": "function", "function_name": "la_mat_ma", "args": [123], "expected": False},
            {"name": "555 trùng chữ số", "mode": "function", "function_name": "la_mat_ma", "args": [555], "expected": False},
            {"name": "690 trăm < chục", "mode": "function", "function_name": "la_mat_ma", "args": [690], "expected": False},
            {"name": "Danh sách đủ 6 mã", "mode": "function", "function_name": "tim_mat_ma", "args": [], "expected": [645, 735, 825, 870, 915, 960]},
        ],
        "order_num": 2,
    })

    questions.append({
        "type": "python_code",
        "content": (
            "Câu 4 — CHÀO THEO TÊN\n\n"
            "Nhập họ tên của một học sinh. In ra lời chào theo mẫu:\n"
            "Xin chao, Phu!\n"
            "(lấy tên cuối cùng trong họ tên đã nhập).\n\n"
            "Ví dụ: Nhập Tran Quang Phu → Xin chao, Phu!\n\n"
            "Yêu cầu chấm tự động — viết hàm chao(ho_ten) "
            "trả về đúng chuỗi lời chào.\n\n"
            "Ví dụ:\n"
            'chao("Tran Quang Phu") → "Xin chao, Phu!"\n'
            'chao("Le Thi Mai") → "Xin chao, Mai!"\n'
            'chao("Phu") → "Xin chao, Phu!"'
        ),
        "points": 20,
        "allow_run": True,
        "function_name": "chao",
        "hint": (
            'ten = ho_ten.strip().split()[-1]; return f"Xin chao, {ten}!"'
        ),
        "starter_code": (
            "def chao(ho_ten):\n"
            "    # Lay ten cuoi cung, tra ve 'Xin chao, Ten!'\n"
            "    pass\n\n"
            '# Thu: print(chao("Tran Quang Phu"))  # Xin chao, Phu!\n'
            '# ho_ten = input("Nhap ho ten: ")\n'
            "# print(chao(ho_ten))\n"
        ),
        "testcases": [
            {"name": "Tran Quang Phu", "mode": "function", "function_name": "chao", "args": ["Tran Quang Phu"], "expected": "Xin chao, Phu!"},
            {"name": "Le Thi Mai", "mode": "function", "function_name": "chao", "args": ["Le Thi Mai"], "expected": "Xin chao, Mai!"},
            {"name": "Một từ Phu", "mode": "function", "function_name": "chao", "args": ["Phu"], "expected": "Xin chao, Phu!"},
            {"name": "Thừa khoảng trắng", "mode": "function", "function_name": "chao", "args": ["  Nguyen Van An  "], "expected": "Xin chao, An!"},
            {"name": "Bốn tiếng", "mode": "function", "function_name": "chao", "args": ["Tran Van Quang Phu"], "expected": "Xin chao, Phu!"},
        ],
        "order_num": 3,
    })

    questions.append({
        "type": "python_code",
        "content": (
            "Câu 5 — ĐẾM KÝ TỰ\n\n"
            "Nhập một câu bất kỳ. Viết chương trình đếm tổng số ký tự của câu, "
            "bao gồm cả dấu cách.\n\n"
            "Ví dụ:\n"
            'Nhập "Thay Phu Anex" → 13\n'
            'Nhập "Lap trinh Python" → 16\n\n'
            "Yêu cầu chấm tự động — viết hàm dem_ky_tu(cau) trả về số nguyên.\n\n"
            "Ví dụ:\n"
            'dem_ky_tu("Thay Phu Anex") → 13\n'
            'dem_ky_tu("Lap trinh Python") → 16\n'
            'dem_ky_tu("a") → 1'
        ),
        "points": 20,
        "allow_run": True,
        "function_name": "dem_ky_tu",
        "hint": "return len(cau)  — len() đếm mọi ký tự, kể cả dấu cách.",
        "starter_code": (
            "def dem_ky_tu(cau):\n"
            "    # Tra ve tong so ky tu, ke ca dau cach\n"
            "    pass\n\n"
            '# Thu: print(dem_ky_tu("Thay Phu Anex"))  # 13\n'
            '# cau = input("Nhap cau: ")\n'
            "# print(dem_ky_tu(cau))\n"
        ),
        "testcases": [
            {"name": "Thay Phu Anex → 13", "mode": "function", "function_name": "dem_ky_tu", "args": ["Thay Phu Anex"], "expected": 13},
            {"name": "Lap trinh Python → 16", "mode": "function", "function_name": "dem_ky_tu", "args": ["Lap trinh Python"], "expected": 16},
            {"name": "Một ký tự", "mode": "function", "function_name": "dem_ky_tu", "args": ["a"], "expected": 1},
            {"name": "Hai dấu cách", "mode": "function", "function_name": "dem_ky_tu", "args": ["  "], "expected": 2},
            {"name": "Rỗng", "mode": "function", "function_name": "dem_ky_tu", "args": [""], "expected": 0},
            {"name": "Xin chao, Phu!", "mode": "function", "function_name": "dem_ky_tu", "args": ["Xin chao, Phu!"], "expected": 15},
        ],
        "order_num": 4,
    })

    return questions


def main():
    app = create_app()
    with app.app_context():
        questions = sanitize_questions(build_questions())
        description = (
            "Bài kiểm tra Python 25/10 — 5 câu tự luận: "
            "Cửa hàng nước · Số chẵn 1..n · Mật mã két · Chào theo tên · Đếm ký tự. "
            "Chấm bằng testcase (hàm)."
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
        mc = sum(1 for q in data["questions"] if q.get("type") == "mcq")
        tl = sum(1 for q in data["questions"] if q.get("type") == "python_code")
        pts = sum(int(q.get("points") or 0) for q in data["questions"])
        print(f"mcq={mc} code={tl} total_points={pts}")
        print(f"public=/quiz/{data['slug']}")


if __name__ == "__main__":
    main()
