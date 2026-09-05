"""Seed: Kiểm tra Python ngày 30-08 — 25 trắc nghiệm + 3 tự luận code."""

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions

QUIZ_TITLE = "Kiểm tra Python ngày 30-08"


def mcq(num, content, options, correct_idx, explanation=""):
    opts = [{"text": t, "is_correct": i == correct_idx} for i, t in enumerate(options)]
    q = {
        "type": "mcq",
        "content": f"Câu {num}: {content}",
        "points": 1,
        "options": opts,
        "order_num": num - 1,
    }
    if explanation.strip():
        q["explanation"] = explanation.strip()
    return q


RAW = [
    mcq(
        1,
        "Phương thức nào thường được sử dụng để thêm một phần tử vào cuối list?",
        ["add()", "insertEnd()", "append()", "push()"],
        2,
        """A. add() – Sai: Thường dùng với set.
B. insertEnd() – Sai: Không phải phương thức của list.
C. append() – Đúng: Thêm phần tử vào cuối list.
D. push() – Sai: Không có trong list Python.""",
    ),
    mcq(
        2,
        "Kiểu dữ liệu int dùng để biểu diễn loại dữ liệu nào?",
        ["Số nguyên", "Số thực", "Chuỗi ký tự", "Đúng/Sai"],
        0,
        """A. Số nguyên – Đúng: int lưu số nguyên như 5, -3, 100.
B. Số thực – Sai: Dùng float.
C. Chuỗi ký tự – Sai: Dùng str.
D. Đúng/Sai – Sai: Dùng bool.""",
    ),
    mcq(
        3,
        "Lệnh nào dùng để in dữ liệu ra màn hình trong Python?",
        ["input()", "print()", "show()", "output()"],
        1,
        """A. input() – Sai: Nhập dữ liệu.
B. print() – Đúng: In ra màn hình.
C. show() – Sai: Không phải hàm cơ bản.
D. output() – Sai: Không phải hàm cơ bản.""",
    ),
    mcq(
        4,
        "Vòng lặp while tiếp tục thực hiện khi nào?",
        ["Khi điều kiện còn đúng", "Khi điều kiện sai", "Chỉ thực hiện đúng một lần", "Khi chương trình kết thúc"],
        0,
        """A. Khi điều kiện còn đúng – Đúng: while lặp khi điều kiện True.
B. Khi điều kiện sai – Sai.
C. Chỉ một lần – Sai.
D. Khi kết thúc – Sai.""",
    ),
    mcq(
        5,
        "Kiểu dữ liệu str dùng để lưu gì?",
        ["Số nguyên", "Số thực", "Chuỗi ký tự", "Giá trị True/False"],
        2,
        """A. Số nguyên – Sai.
B. Số thực – Sai.
C. Chuỗi ký tự – Đúng: str lưu text như "Hello".
D. True/False – Sai: Dùng bool.""",
    ),
    mcq(
        6,
        "Từ khóa nào được sử dụng để định nghĩa một hàm trong Python?",
        ["function", "func", "def", "method"],
        2,
        """A. function – Sai.
B. func – Sai.
C. def – Đúng.
D. method – Sai.""",
    ),
    mcq(
        7,
        "Biến trong Python dùng để làm gì?",
        ["Lưu trữ dữ liệu", "Chỉ để in dữ liệu", "Chỉ để tạo vòng lặp", "Xóa chương trình"],
        0,
        """A. Lưu trữ dữ liệu – Đúng.
B. Chỉ in – Sai.
C. Chỉ vòng lặp – Sai.
D. Xóa chương trình – Sai.""",
    ),
    mcq(
        8,
        "Python là loại ngôn ngữ lập trình nào?",
        ["Ngôn ngữ máy", "Ngôn ngữ thông dịch", "Ngôn ngữ đánh dấu", "Ngôn ngữ truy vấn"],
        1,
        """A. Ngôn ngữ máy – Sai.
B. Ngôn ngữ thông dịch – Đúng: Mã nguồn được thực thi qua trình thông dịch Python.
C. Ngôn ngữ đánh dấu – Sai.
D. Ngôn ngữ truy vấn – Sai: Ví dụ SQL.""",
    ),
    mcq(
        9,
        "Ký hiệu nào được sử dụng để viết chú thích một dòng trong Python?",
        ["//", "<!-- -->", "#", "/* */"],
        2,
        """A. // – Sai: Dùng trong C/Java.
B. <!-- --> – Sai: Dùng trong HTML.
C. # – Đúng: Chú thích một dòng trong Python.
D. /* */ – Sai: Dùng trong C/Java.""",
    ),
    mcq(
        10,
        "List trong Python dùng để làm gì?",
        ["Lưu trữ nhiều phần tử", "Chỉ lưu một số nguyên", "Chỉ lưu giá trị True/False", "Tạo một hàm"],
        0,
        """A. Lưu nhiều phần tử – Đúng: list như [1, 2, 3].
B. Một số nguyên – Sai.
C. True/False – Sai.
D. Tạo hàm – Sai.""",
    ),
    mcq(
        11,
        "Hàm input() trong Python có chức năng gì?",
        ["Xuất dữ liệu", "Nhập dữ liệu từ người dùng", "Xóa dữ liệu", "Tạo một biến"],
        1,
        """A. Xuất dữ liệu – Sai: Dùng print().
B. Nhập dữ liệu – Đúng.
C. Xóa dữ liệu – Sai.
D. Tạo biến – Sai.""",
    ),
    mcq(
        12,
        "Ai là người tạo ra ngôn ngữ lập trình Python?",
        ["Bill Gates", "James Gosling", "Guido van Rossum", "Dennis Ritchie"],
        2,
        """A. Bill Gates – Sai: Microsoft.
B. James Gosling – Sai: Java.
C. Guido van Rossum – Đúng: Người tạo Python.
D. Dennis Ritchie – Sai: Ngôn ngữ C.""",
    ),
    mcq(
        13,
        "Toán tử nào trong Python được sử dụng để thực hiện phép chia lấy phần nguyên?",
        ["/", "//", "%", "**"],
        1,
        """A. / – Sai: Phép chia thường.
B. // – Đúng: Chia lấy phần nguyên. Ví dụ: 10 // 3 = 3.
C. % – Sai: Lấy phần dư.
D. ** – Sai: Lũy thừa.""",
    ),
    mcq(
        14,
        "Cấu trúc nào dùng để thực hiện câu lệnh khi một điều kiện đúng?",
        ["if", "for", "while", "import"],
        0,
        """A. if – Đúng: Rẽ nhánh theo điều kiện.
B. for – Sai: Vòng lặp.
C. while – Sai: Vòng lặp.
D. import – Sai: Nhập thư viện.""",
    ),
    mcq(
        15,
        "Từ khóa import trong Python thường được sử dụng để làm gì?",
        ["Xóa một biến", "Nhập module hoặc thư viện", "Tạo vòng lặp", "Tạo một class"],
        1,
        """A. Xóa biến – Sai.
B. Nhập module – Đúng: Ví dụ import math.
C. Vòng lặp – Sai.
D. Class – Sai.""",
    ),
    mcq(
        16,
        "Kiểu dữ liệu float dùng để biểu diễn loại dữ liệu nào?",
        ["Số nguyên", "Số thực", "Chuỗi ký tự", "Giá trị đúng/sai"],
        1,
        """A. Số nguyên – Sai: int.
B. Số thực – Đúng: Ví dụ 3.14.
C. Chuỗi – Sai: str.
D. Đúng/sai – Sai: bool.""",
    ),
    mcq(
        17,
        "Toán tử nào trong Python dùng để lấy phần dư của phép chia?",
        ["/", "//", "%", "**"],
        2,
        """A. / – Sai: Phép chia.
B. // – Sai: Chia lấy phần nguyên.
C. % – Đúng: Lấy phần dư. Ví dụ: 10 % 3 = 1.
D. ** – Sai: Lũy thừa.""",
    ),
    mcq(
        18,
        "Từ khóa nào được sử dụng để tạo một lớp (class) trong Python?",
        ["object", "class", "struct", "new"],
        1,
        """A. object – Sai: Lớp cơ sở.
B. class – Đúng.
C. struct – Sai.
D. new – Sai.""",
    ),
    mcq(
        19,
        "Python được phát hành lần đầu tiên vào năm nào?",
        ["1989", "1991", "1995", "2000"],
        1,
        """A. 1989 – Sai: Năm bắt đầu phát triển.
B. 1991 – Đúng: Phiên bản đầu tiên công bố.
C. 1995 – Sai.
D. 2000 – Sai.""",
    ),
    mcq(
        20,
        "Vòng lặp for thường được sử dụng để làm gì?",
        ["Kiểm tra kiểu dữ liệu", "Lặp lại một nhóm câu lệnh", "Khai báo thư viện", "Tạo chuỗi"],
        1,
        """A. Kiểm tra kiểu – Sai.
B. Lặp câu lệnh – Đúng.
C. Thư viện – Sai.
D. Tạo chuỗi – Sai.""",
    ),
    mcq(
        21,
        "Hai giá trị của kiểu dữ liệu bool là gì?",
        ["Yes và No", "1 và 2", "True và False", "On và Off"],
        2,
        """A. Yes/No – Sai.
B. 1 và 2 – Sai.
C. True và False – Đúng.
D. On/Off – Sai.""",
    ),
    mcq(
        22,
        "Toán tử nào trong Python được sử dụng để kiểm tra hai giá trị có bằng nhau hay không?",
        ["=", "==", "!=", "=>"],
        1,
        """A. = – Sai: Gán giá trị.
B. == – Đúng: So sánh bằng.
C. != – Sai: So sánh khác.
D. => – Sai: Không hợp lệ.""",
    ),
    mcq(
        23,
        "Hàm (function) trong Python có mục đích chính là gì?",
        [
            "Nhóm các câu lệnh để thực hiện một nhiệm vụ",
            "Chỉ dùng để lưu dữ liệu",
            "Chỉ dùng để tạo biến",
            "Xóa chương trình",
        ],
        0,
        """A. Nhóm câu lệnh – Đúng: Tái sử dụng code.
B. Chỉ lưu dữ liệu – Sai.
C. Chỉ tạo biến – Sai.
D. Xóa chương trình – Sai.""",
    ),
    mcq(
        24,
        "Trong Python, câu lệnh return trong hàm dùng để làm gì?",
        ["Lặp lại hàm", "Kết thúc chương trình", "Trả về một giá trị từ hàm", "Tạo một biến mới"],
        2,
        """A. Lặp hàm – Sai.
B. Kết thúc chương trình – Sai.
C. Trả về giá trị – Đúng: return kết quả từ hàm.
D. Tạo biến – Sai.""",
    ),
    mcq(
        25,
        "Phần mở rộng thường dùng của tệp Python là gì?",
        [".java", ".cpp", ".py", ".html"],
        2,
        """A. .java – Sai.
B. .cpp – Sai.
C. .py – Đúng.
D. .html – Sai.""",
    ),
    {
        "type": "python_code",
        "content": (
            "Câu 26 — Kiểm tra số dương, âm hay bằng 0\n\n"
            "Viết chương trình Python nhập vào một số nguyên n.\n"
            "Kiểm tra và in ra n là số dương, số âm hay bằng 0."
        ),
        "points": 5,
        "allow_run": True,
        "hint": "Dùng if / elif / else: n > 0, n < 0, n == 0.",
        "starter_code": (
            'n = int(input("Nhap n: "))\n\n'
            "# Kiem tra va in ket qua tai day\n"
        ),
        "order_num": 25,
    },
    {
        "type": "python_code",
        "content": (
            "Câu 27 — Tìm số lớn nhất\n\n"
            "Viết chương trình Python nhập vào 3 số nguyên a, b, c.\n"
            "Tìm và in ra số lớn nhất trong 3 số."
        ),
        "points": 5,
        "allow_run": True,
        "hint": "Dùng max(a, b, c) hoặc so sánh từng cặp bằng if.",
        "starter_code": (
            'a = int(input("Nhap a: "))\n'
            'b = int(input("Nhap b: "))\n'
            'c = int(input("Nhap c: "))\n\n'
            "# Tim va in so lon nhat tai day\n"
        ),
        "order_num": 26,
    },
    {
        "type": "python_code",
        "content": (
            "Câu 28 — Đếm số chẵn và số lẻ\n\n"
            "Viết chương trình nhập vào n (số lượng phần tử), "
            "sau đó nhập n số nguyên.\n"
            "Kiểm tra và in ra có bao nhiêu số chẵn và bao nhiêu số lẻ trong danh sách."
        ),
        "points": 5,
        "allow_run": True,
        "hint": (
            "Dùng vòng for nhập n số. "
            "Số chẵn: n % 2 == 0. Dùng biến dem_chan, dem_le."
        ),
        "starter_code": (
            'n = int(input("Nhap n: "))\n\n'
            "# Nhap n so va dem chan/le tai day\n"
        ),
        "order_num": 27,
    },
]


def main():
    app = create_app()
    with app.app_context():
        existing = col("quizzes").find_one({"title": QUIZ_TITLE})
        questions = sanitize_questions(RAW)
        description = (
            "Bài kiểm tra Python ngày 30/08 — 25 câu trắc nghiệm + 3 câu tự luận viết code. "
            "Giải thích trắc nghiệm chỉ hiển thị khi admin đăng nhập và chọn đáp án."
        )
        now = datetime.utcnow()

        if existing:
            col("quizzes").update_one(
                {"_id": existing["_id"]},
                {
                    "$set": {
                        "questions": questions,
                        "description": description,
                        "duration_minutes": 45,
                        "is_active": True,
                        "updated_at": now,
                    }
                },
            )
            existing["questions"] = questions
            data = quiz_to_dict(existing, include_answers=True)
            print("UPDATED")
        else:
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
        print(f"max_score={data['max_score']}")
        print(f"public=/quiz/{data['slug']}")


if __name__ == "__main__":
    main()
