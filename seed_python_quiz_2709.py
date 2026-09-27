"""Seed: Bài kiểm tra Python 27/09 — 4 câu tự luận."""

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions

QUIZ_TITLE = "Bài kiểm tra Python ngày 27-09"
FIXED_SLUG = "python-2709"


def build_questions():
    return [
        {
            "type": "python_code",
            "content": (
                "Câu 1. Tính tổng\n\n"
                "Viết chương trình tính tổng:\n\n"
                "S = 1 + 2 + 3 + ... + 1000\n\n"
                "Yêu cầu chấm tự động: viết hàm tinh_tong() không tham số, "
                "trả về (return) giá trị tổng S.\n\n"
                "Ví dụ: tinh_tong() → 500500"
            ),
            "points": 25,
            "allow_run": True,
            "function_name": "tinh_tong",
            "hint": "return sum(range(1, 1001)) hoặc dùng vòng for cộng dồn.",
            "starter_code": (
                "def tinh_tong():\n"
                "    # Tinh S = 1 + 2 + ... + 1000 va return\n"
                "    pass\n\n"
                "# Thu: print(tinh_tong())  # 500500\n"
            ),
            "testcases": [
                {
                    "name": "Tong 1..1000",
                    "mode": "function",
                    "function_name": "tinh_tong",
                    "args": [],
                    "expected": 500500,
                },
            ],
            "order_num": 0,
        },
        {
            "type": "python_code",
            "content": (
                "Câu 2. Quản lý danh sách truyện\n\n"
                "Viết chương trình tạo một danh sách truyện, thực hiện các chức năng:\n\n"
                "1. Thêm truyện vào danh sách.\n"
                "2. Tìm kiếm truyện theo tên.\n"
                "3. In toàn bộ danh sách truyện.\n"
                "4. Thoát chương trình.\n\n"
                "Chương trình sử dụng menu và chạy liên tục cho đến khi người dùng chọn thoát.\n\n"
                "(Câu này giáo viên chấm thủ công — em có thể bấm Chạy thử và nhập menu.)"
            ),
            "points": 25,
            "allow_run": True,
            "hint": (
                "Dùng list + while True + if/elif theo lựa chọn. "
                "Thêm: append. Tìm: for + if ten in ... In: for print."
            ),
            "starter_code": (
                "ds_truyen = []\n\n"
                "while True:\n"
                '    print("===== MENU =====")\n'
                '    print("1. Them truyen")\n'
                '    print("2. Tim kiem theo ten")\n'
                '    print("3. In danh sach")\n'
                '    print("4. Thoat")\n'
                '    chon = input("Chon: ")\n\n'
                '    if chon == "1":\n'
                "        # Them truyen\n"
                "        pass\n"
                '    elif chon == "2":\n'
                "        # Tim kiem\n"
                "        pass\n"
                '    elif chon == "3":\n'
                "        # In danh sach\n"
                "        pass\n"
                '    elif chon == "4":\n'
                '        print("Tam biet!")\n'
                "        break\n"
            ),
            "order_num": 1,
        },
        {
            "type": "python_code",
            "content": (
                "Câu 3. Xây dựng lớp Truyện\n\n"
                "Tạo lớp Truyen gồm các thông tin:\n"
                "- Mã truyện\n"
                "- Tên truyện\n"
                "- Tác giả\n"
                "- Đơn giá\n\n"
                "Tạo phương thức tinh_tien(so_luong) tính thành tiền theo công thức:\n\n"
                "Thành tiền = Số lượng × Đơn giá\n\n"
                "Yêu cầu: dùng đúng tên class Truyen và method tinh_tien "
                "(return số tiền, không bắt buộc print)."
            ),
            "points": 25,
            "allow_run": True,
            "hint": "return so_luong * self.don_gia",
            "starter_code": (
                "class Truyen:\n"
                "    def __init__(self, ma, ten, tac_gia, don_gia):\n"
                "        self.ma = ma\n"
                "        self.ten = ten\n"
                "        self.tac_gia = tac_gia\n"
                "        self.don_gia = don_gia\n\n"
                "    def tinh_tien(self, so_luong):\n"
                "        # Thanh tien = so_luong * don_gia\n"
                "        pass\n\n"
                '# Thu: t = Truyen("T01", "Doraemon", "Fujiko", 25000)\n'
                "# print(t.tinh_tien(2))  # 50000\n"
            ),
            "testcases": [
                {
                    "name": "2 cuốn × 25000",
                    "mode": "class_method",
                    "class_name": "Truyen",
                    "constructor_args": ["T01", "Doraemon", "Fujiko", 25000],
                    "method": "tinh_tien",
                    "method_args": [2],
                    "expected": 50000,
                },
                {
                    "name": "1 cuốn × 10000",
                    "mode": "class_method",
                    "class_name": "Truyen",
                    "constructor_args": ["T02", "Conan", "Aoyama", 10000],
                    "method": "tinh_tien",
                    "method_args": [1],
                    "expected": 10000,
                },
                {
                    "name": "5 cuốn × 15000",
                    "mode": "class_method",
                    "class_name": "Truyen",
                    "constructor_args": ["T03", "One Piece", "Oda", 15000],
                    "method": "tinh_tien",
                    "method_args": [5],
                    "expected": 75000,
                },
            ],
            "order_num": 2,
        },
        {
            "type": "python_code",
            "content": (
                "Câu 4. Quản lý tài khoản bằng File\n\n"
                "Tạo file taikhoan.txt để lưu thông tin tài khoản.\n\n"
                "Viết chương trình có các chức năng:\n\n"
                "1. Đăng ký: Nhập tên đăng nhập và mật khẩu, sau đó ghi tài khoản vào file.\n"
                "2. Đăng nhập: Nhập tên đăng nhập và mật khẩu, kiểm tra thông tin có tồn tại "
                "trong file hay không.\n"
                "   - Nếu tài khoản và mật khẩu chính xác thì thông báo đăng nhập thành công.\n"
                "   - Nếu không chính xác thì thông báo đăng nhập thất bại.\n"
                "3. Không cho phép đăng ký tài khoản đã tồn tại.\n\n"
                "(Câu này giáo viên chấm thủ công — em chạy thử với file mẫu taikhoan.txt.)"
            ),
            "points": 25,
            "allow_run": True,
            "hint": (
                "Đăng ký: đọc file kiểm tra trùng user, rồi ghi thêm dòng. "
                "Đăng nhập: đọc từng dòng so sánh user/pass. "
                "Gợi ý lưu dạng: username,password mỗi dòng."
            ),
            "starter_code": (
                'FILE = "taikhoan.txt"\n\n'
                "def dang_ky():\n"
                "    # Nhap user/pass, kiem tra trung, ghi file\n"
                "    pass\n\n"
                "def dang_nhap():\n"
                "    # Nhap user/pass, kiem tra trong file\n"
                "    pass\n\n"
                "while True:\n"
                '    print("===== TAI KHOAN =====")\n'
                '    print("1. Dang ky")\n'
                '    print("2. Dang nhap")\n'
                '    print("3. Thoat")\n'
                '    chon = input("Chon: ")\n'
                '    if chon == "1":\n'
                "        dang_ky()\n"
                '    elif chon == "2":\n'
                "        dang_nhap()\n"
                '    elif chon == "3":\n'
                '        print("Tam biet!")\n'
                "        break\n"
            ),
            "sample_files": [
                {"name": "taikhoan.txt", "content": ""},
            ],
            "order_num": 3,
        },
    ]


def main():
    app = create_app()
    with app.app_context():
        questions = sanitize_questions(build_questions())
        description = (
            "Bài kiểm tra Python 27/09 — 4 câu tự luận: "
            "Tổng 1..1000 · DS truyện (menu) · Lớp Truyen · File tài khoản. "
            "Câu 1 & 3 chấm testcase; câu 2 & 4 giáo viên chấm thủ công."
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
