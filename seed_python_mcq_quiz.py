"""Seed: Kiểm tra Python Trắc nghiệm — 30 câu (cơ bản + list, hàm, class, file, vòng lặp, if)."""

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions

QUIZ_TITLE = "Kiểm tra Python Trắc nghiệm — 30 câu"


def mcq(num, content, options, correct_idx, explanation):
    opts = [{"text": t, "is_correct": i == correct_idx} for i, t in enumerate(options)]
    return {
        "type": "mcq",
        "content": f"Câu {num}: {content}",
        "points": 1,
        "options": opts,
        "explanation": explanation.strip(),
        "order_num": num - 1,
    }


RAW = [
    mcq(
        1,
        "Python là loại ngôn ngữ lập trình nào?",
        ["Ngôn ngữ máy", "Ngôn ngữ thông dịch", "Ngôn ngữ biên dịch", "Ngôn ngữ truy vấn"],
        1,
        """A. Ngôn ngữ máy – Sai: Ngôn ngữ máy dùng mã nhị phân 0 và 1, CPU thực hiện trực tiếp.
B. Ngôn ngữ thông dịch – Đúng: Python được thực thi qua Python Interpreter.
C. Ngôn ngữ biên dịch – Sai: Ví dụ C, C++ dùng compiler chuyển mã nguồn trước khi chạy.
D. Ngôn ngữ truy vấn – Sai: Ví dụ SQL dùng cho cơ sở dữ liệu.

Kết luận: Python thường được phân loại là ngôn ngữ thông dịch.""",
    ),
    mcq(
        2,
        "Python được phát triển bởi ai?",
        ["Bill Gates", "James Gosling", "Guido van Rossum", "Dennis Ritchie"],
        2,
        """A. Bill Gates – Sai: Đồng sáng lập Microsoft.
B. James Gosling – Sai: Người tạo Java.
C. Guido van Rossum – Đúng: Người tạo Python (cuối thập niên 1980).
D. Dennis Ritchie – Sai: Người phát triển ngôn ngữ C.

Kết luận: Người tạo Python là Guido van Rossum.""",
    ),
    mcq(
        3,
        "Phần mở rộng của tệp chương trình Python thường là gì?",
        [".java", ".cpp", ".py", ".html"],
        2,
        """A. .java – Sai: Tệp Java.
B. .cpp – Sai: Tệp C++.
C. .py – Đúng: Phần mở rộng tiêu chuẩn, ví dụ bai1.py.
D. .html – Sai: Tệp HTML.

Kết luận: Tệp Python thường có phần mở rộng .py.""",
    ),
    mcq(
        4,
        "Đâu là cách đặt tên biến đúng trong Python?",
        ["2diem", "diem-so", "diem_so", "diem so"],
        2,
        """Tên biến có thể chứa chữ cái, chữ số và _, không bắt đầu bằng số, không có khoảng trắng.
A. 2diem – Sai: Không được bắt đầu bằng chữ số.
B. diem-so – Sai: Dấu - là toán tử trừ.
C. diem_so – Đúng: Hợp lệ.
D. diem so – Sai: Có khoảng trắng.

Kết luận: diem_so là tên biến hợp lệ.""",
    ),
    mcq(
        5,
        "Tên biến nào sau đây không hợp lệ trong Python?",
        ["ho_ten", "diemToan", "_diem", "10diem"],
        3,
        """A. ho_ten – Hợp lệ.
B. diemToan – Hợp lệ.
C. _diem – Hợp lệ (có thể bắt đầu bằng _).
D. 10diem – Sai: Không được bắt đầu bằng chữ số.

Kết luận: 10diem không hợp lệ.""",
    ),
    mcq(
        6,
        "Tên biến nào sau đây hợp lệ trong Python?",
        ["ho ten", "ho-ten", "ho_ten", "ho@ten"],
        2,
        """A. ho ten – Sai: Có khoảng trắng.
B. ho-ten – Sai: Có dấu -.
C. ho_ten – Đúng.
D. ho@ten – Sai: @ không được phép.

Kết luận: ho_ten hợp lệ.""",
    ),
    mcq(
        7,
        "Tên nào sau đây không thể sử dụng làm tên biến trong Python?",
        ["student", "student_name", "class", "student1"],
        2,
        """A. student – Hợp lệ.
B. student_name – Hợp lệ.
C. class – Sai: class là từ khóa Python.
D. student1 – Hợp lệ.

Kết luận: Không dùng từ khóa Python làm tên biến.""",
    ),
    mcq(
        8,
        "Lệnh nào dùng để hiển thị dữ liệu ra màn hình?",
        ["input()", "print()", "show()", "display()"],
        1,
        """A. input() – Sai: Nhận dữ liệu từ người dùng.
B. print() – Đúng: Xuất dữ liệu ra màn hình.
C. show() – Sai: Không phải hàm cơ bản của Python.
D. display() – Sai: Không phải hàm in cơ bản.

Ví dụ: print("Xin chao") → Xin chao
Kết luận: Dùng print() để hiển thị dữ liệu.""",
    ),
    mcq(
        9,
        "Lệnh nào dùng để nhập dữ liệu từ bàn phím?",
        ["get()", "scan()", "input()", "read()"],
        2,
        """A. get() – Sai.
B. scan() – Sai.
C. input() – Đúng: Nhập dữ liệu từ bàn phím.
D. read() – Sai: Thường dùng đọc tệp.

Ví dụ: ten = input("Nhap ten: ")
Kết luận: Sử dụng input().""",
    ),
    mcq(
        10,
        "Đâu là cách gán giá trị đúng cho biến x?",
        ["x == 10", "x = 10", "int x = 10", "10 = x"],
        1,
        """A. x == 10 – Sai: == là so sánh.
B. x = 10 – Đúng: Gán giá trị.
C. int x = 10 – Sai: Không phải cú pháp Python.
D. 10 = x – Sai: Không gán được cho hằng số.

Kết luận: x = 10 là cú pháp gán đúng.""",
    ),
    mcq(
        11,
        "Giá trị 15 thuộc kiểu dữ liệu nào trong Python?",
        ["str", "float", "int", "bool"],
        2,
        """A. str – Sai: Chuỗi, ví dụ "15".
B. float – Sai: Số thực, ví dụ 15.5.
C. int – Đúng: Số nguyên.
D. bool – Sai: True/False.

Kết luận: 15 thuộc kiểu int.""",
    ),
    mcq(
        12,
        'Giá trị "Hello Python" thuộc kiểu dữ liệu nào?',
        ["int", "str", "float", "bool"],
        1,
        """A. int – Sai.
B. str – Đúng: Chuỗi trong dấu nháy.
C. float – Sai.
D. bool – Sai.

Kết luận: "Hello Python" có kiểu str.""",
    ),
    mcq(
        13,
        "Toán tử nào dùng để tính phần dư trong Python?",
        ["/", "//", "%", "**"],
        2,
        """A. / – Sai: Phép chia (thường ra số thực).
B. // – Sai: Chia lấy phần nguyên.
C. % – Đúng: Chia lấy phần dư.
D. ** – Sai: Lũy thừa.

Ví dụ: 10 % 3 = 1
Kết luận: Toán tử lấy phần dư là %.""",
    ),
    mcq(
        14,
        "Toán tử nào được sử dụng để tính lũy thừa trong Python?",
        ["^", "**", "//", "%%"],
        1,
        """A. ^ – Sai: XOR theo bit.
B. ** – Đúng: Lũy thừa.
C. // – Sai: Chia lấy phần nguyên.
D. %% – Sai: Không hợp lệ.

Ví dụ: 2 ** 3 = 8
Kết luận: Toán tử lũy thừa là **.""",
    ),
    mcq(
        15,
        "Kết quả của chương trình sau là gì?\n\na = 5\nb = 3\nprint(a + b)",
        ["2", "8", "15", "53"],
        1,
        """A. 2 – Sai: Kết quả của 5 - 3.
B. 8 – Đúng: 5 + 3 = 8.
C. 15 – Sai: Kết quả của 5 × 3.
D. 53 – Sai: Ghép chuỗi, nhưng a, b là số nguyên.

Kết luận: Chương trình in ra 8.""",
    ),
    mcq(
        16,
        "Kiểu dữ liệu nào trong Python dùng để lưu một dãy nhiều phần tử và có thể thay đổi được?",
        ["tuple", "list", "str", "int"],
        1,
        """A. tuple – Sai: Không thay đổi được sau khi tạo.
B. list – Đúng: Có thể thêm, xóa, sửa phần tử.
C. str – Sai: Chuỗi ký tự.
D. int – Sai: Số nguyên.

Ví dụ: ds = [10, 20, 30]; ds.append(40)""",
    ),
    mcq(
        17,
        "Đâu là cách tạo một danh sách (list) đúng trong Python?",
        ["ds = (1, 2, 3)", "ds = {1, 2, 3}", "ds = [1, 2, 3]", "ds = <1, 2, 3>"],
        2,
        """A. () – Sai: Tạo tuple.
B. {} – Sai: Tạo set.
C. [] – Đúng: Tạo list.
D. <> – Sai: Không phải cú pháp Python.""",
    ),
    mcq(
        18,
        "Phần tử đầu tiên của list trong Python có chỉ số (index) là bao nhiêu?",
        ["0", "1", "-1", "2"],
        0,
        """Python đếm index từ 0.
Ví dụ: ds = ["A", "B", "C"] → ds[0] = "A"
A. 0 – Đúng.
B. 1 – Sai: Phần tử thứ hai.
C. -1 – Sai: Phần tử cuối.
D. 2 – Sai: Phần tử thứ ba.""",
    ),
    mcq(
        19,
        "Phương thức nào dùng để thêm một phần tử vào cuối list?",
        ["add()", "insert()", "append()", "push()"],
        2,
        """A. add() – Sai: Thường dùng với set.
B. insert() – Sai: Thêm vào vị trí chỉ định.
C. append() – Đúng: Thêm vào cuối list.
D. push() – Sai: Không có trong list Python.

Ví dụ: ds = [1,2,3]; ds.append(4) → [1,2,3,4]""",
    ),
    mcq(
        20,
        "Từ khóa nào được sử dụng để định nghĩa một hàm trong Python?",
        ["function", "func", "def", "method"],
        2,
        """A. function – Sai.
B. func – Sai.
C. def – Đúng.
D. method – Sai.

Ví dụ: def chao(): print("Xin chao")""",
    ),
    mcq(
        21,
        "Trong hàm Python, từ khóa nào được sử dụng để trả về một giá trị?",
        ["return", "output", "send", "result"],
        0,
        """A. return – Đúng.
B. output – Sai.
C. send – Sai.
D. result – Sai.

Ví dụ: def tong(a, b): return a + b""",
    ),
    mcq(
        22,
        "Đoạn chương trình sau trả về kết quả nào?\n\ndef tong(a, b):\n    return a + b\n\nprint(tong(3, 5))",
        ["3", "5", "8", "15"],
        2,
        """A. 3 – Sai: Chỉ là tham số a.
B. 5 – Sai: Chỉ là tham số b.
C. 8 – Đúng: 3 + 5 = 8.
D. 15 – Sai: 3 × 5.""",
    ),
    mcq(
        23,
        "Từ khóa nào được sử dụng để tạo một lớp (class) trong Python?",
        ["object", "class", "struct", "new"],
        1,
        """A. object – Sai: Lớp cơ sở, không dùng để định nghĩa class.
B. class – Đúng.
C. struct – Sai.
D. new – Sai.

Ví dụ: class HocSinh: pass""",
    ),
    mcq(
        24,
        "Trong lập trình hướng đối tượng, class được hiểu là gì?",
        ["Một biến", "Một vòng lặp", "Một khuôn mẫu để tạo các đối tượng", "Một kiểu dữ liệu chỉ lưu số"],
        2,
        """A. Biến – Sai.
B. Vòng lặp – Sai.
C. Khuôn mẫu tạo đối tượng – Đúng.
D. Chỉ lưu số – Sai.""",
    ),
    mcq(
        25,
        "Lệnh nào được sử dụng để mở một tệp trong Python?",
        ["open()", "file()", "read()", "load()"],
        0,
        """A. open() – Đúng.
B. file() – Sai.
C. read() – Sai: Đọc nội dung sau khi mở tệp.
D. load() – Sai.

Ví dụ: f = open("data.txt", "r")""",
    ),
    mcq(
        26,
        'Chế độ nào được sử dụng để mở tệp chỉ để đọc dữ liệu?',
        ['"w"', '"a"', '"r"', '"x"'],
        2,
        """A. "w" – Sai: Ghi (có thể ghi đè).
B. "a" – Sai: Ghi thêm.
C. "r" – Đúng: Read — đọc tệp.
D. "x" – Sai: Tạo tệp mới.""",
    ),
    mcq(
        27,
        'Chế độ nào được sử dụng để ghi dữ liệu vào tệp và có thể làm mất nội dung cũ?',
        ['"r"', '"w"', '"a"', '"read"'],
        1,
        """A. "r" – Sai: Đọc.
B. "w" – Đúng: Ghi, xóa nội dung cũ nếu tệp đã tồn tại.
C. "a" – Sai: Ghi thêm cuối tệp.
D. "read" – Sai: Không phải chế độ open().""",
    ),
    mcq(
        28,
        "Vòng lặp nào thường được sử dụng để duyệt qua các phần tử của một list?",
        ["if", "for", "class", "def"],
        1,
        """A. if – Sai: Kiểm tra điều kiện.
B. for – Đúng.
C. class – Sai.
D. def – Sai.

Ví dụ: for x in ds: print(x)""",
    ),
    mcq(
        29,
        "Trong cấu trúc if, điều kiện nào sau đây là đúng cú pháp Python?",
        ["if x > 5:", "if (x > 5)", "if x > 5 then", "if: x > 5"],
        0,
        """A. if x > 5: – Đúng.
B. if (x > 5) – Sai: Thiếu dấu :.
C. if x > 5 then – Sai: Python không có then.
D. if: x > 5 – Sai: : phải đặt sau điều kiện.""",
    ),
    mcq(
        30,
        "Kết quả của chương trình sau là gì?\n\nfor i in range(1, 4):\n    print(i)",
        ["1 2 3", "1 2 3 4", "0 1 2 3", "0 1 2"],
        0,
        """A. 1 2 3 – Đúng: range(1, 4) → 1, 2, 3 (không lấy 4).
B. 1 2 3 4 – Sai: 4 là cận trên, không thuộc dãy.
C. 0 1 2 3 – Sai.
D. 0 1 2 – Sai.""",
    ),
]


def main():
    app = create_app()
    with app.app_context():
        existing = col("quizzes").find_one({"title": QUIZ_TITLE})
        if existing:
            questions = sanitize_questions(RAW)
            col("quizzes").update_one(
                {"_id": existing["_id"]},
                {
                    "$set": {
                        "questions": questions,
                        "description": (
                            "Bài trắc nghiệm Python 30 câu — kiểu dữ liệu, biến, hàm, class, "
                            "list, đọc/ghi file, vòng lặp, if. "
                            "Giải thích chi tiết chỉ hiển thị khi admin đăng nhập và chọn đáp án."
                        ),
                        "duration_minutes": 45,
                        "is_active": True,
                        "updated_at": datetime.utcnow(),
                    }
                },
            )
            existing["questions"] = questions
            data = quiz_to_dict(existing, include_answers=True)
            print("UPDATED")
        else:
            questions = sanitize_questions(RAW)
            slug = None
            for _ in range(20):
                candidate = generate_quiz_slug()
                if not col("quizzes").find_one({"slug": candidate}):
                    slug = candidate
                    break
            if not slug:
                raise RuntimeError("Không tạo được slug")

            now = datetime.utcnow()
            doc = {
                "title": QUIZ_TITLE,
                "description": (
                    "Bài trắc nghiệm Python 30 câu — kiểu dữ liệu, biến, hàm, class, "
                    "list, đọc/ghi file, vòng lặp, if. "
                    "Giải thích chi tiết chỉ hiển thị khi admin đăng nhập và chọn đáp án."
                ),
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
        print(f"public=/quiz/{data['slug']}")


if __name__ == "__main__":
    main()
