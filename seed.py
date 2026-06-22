from datetime import datetime
import random
from bson import ObjectId
from database import col, oid_str
from models import hash_password

SCRATCH_QUESTIONS = [
    {"content": "🐱 Chú mèo Scratch muốn đi từ 🏠 nhà đến 🏫 trường. Bước đầu tiên con sẽ làm gì?", "level": "easy", "category": "sequencing", "answers": ["Mở Scratch và kéo khối 'di chuyển'", "Tắt máy tính", "Vẽ hình tròn", "Xóa dự án"], "correct": 0},
    {"content": "🎨 Trong Scratch, muốn đổi màu nhân vật, con dùng khối nào?", "level": "easy", "category": "observation", "answers": ["Đổi màu 🎨", "Phát âm thanh 🔊", "Xoay 15 độ", "Dừng tất cả"], "correct": 0},
    {"content": "🔢 Nếu mèo đi 10 bước, rồi đi thêm 5 bước nữa, mèo đi tổng bao nhiêu bước?", "level": "easy", "category": "math", "answers": ["15 bước", "5 bước", "10 bước", "20 bước"], "correct": 0},
    {"content": "🔄 Khối lệnh 'lặp lại 4 lần' dùng để làm gì?", "level": "easy", "category": "logic", "answers": ["Làm một việc nhiều lần", "Xóa nhân vật", "Tắt máy", "Đổi nền"], "correct": 0},
    {"content": "▶️ Để bắt đầu chạy chương trình Scratch, con nhấn nút nào?", "level": "easy", "category": "observation", "answers": ["Cờ xanh ▶️", "Cờ đỏ ⏹️", "Nút tắt máy", "Nút in"], "correct": 0},
    {"content": "🧩 Ghép hình: Hình vuông có mấy cạnh bằng nhau?", "level": "easy", "category": "math", "answers": ["4 cạnh", "3 cạnh", "5 cạnh", "6 cạnh"], "correct": 0},
    {"content": "🎵 Muốn mèo kêu 'meow', con thêm khối nào?", "level": "easy", "category": "sequencing", "answers": ["Phát âm thanh meow", "Ẩn nhân vật", "Đổi kích thước", "Dừng chương trình"], "correct": 0},
    {"content": "🌈 Trong Scratch, khối màu 🟦 xanh dương thường dùng để làm gì?", "level": "easy", "category": "observation", "answers": ["Di chuyển nhân vật", "Phát âm thanh", "Đổi nền", "Bắt đầu chương trình"], "correct": 0},
    {"content": "📋 Thứ tự đúng để chạy chương trình Scratch:", "level": "easy", "category": "sequencing", "answers": ["Mở Scratch → Viết lệnh → Nhấn cờ xanh", "Nhấn cờ xanh → Tắt máy → Mở Scratch", "Xóa dự án → Viết lệnh → Mở Scratch", "Tắt máy → Nhấn cờ xanh"], "correct": 0},
    {"content": "🐶 Nhân vật chó 🐕 muốn nhảy lên cao. Khối nào phù hợp nhất?", "level": "easy", "category": "logic", "answers": ["Thay đổi y thêm 50", "Ẩn nhân vật", "Đổi âm thanh", "Xóa khối lệnh"], "correct": 0},
    {"content": "🎯 Nếu điểm số = 0, mỗi lần bắt được 🌟 sao thì +1. Bắt 7 sao thì điểm là?", "level": "medium", "category": "math", "answers": ["7 điểm", "0 điểm", "1 điểm", "10 điểm"], "correct": 0},
    {"content": "🔁 Mèo lặp 'di chuyển 10 bước' 3 lần. Mèo đi tổng bao nhiêu bước?", "level": "medium", "category": "algorithm", "answers": ["30 bước", "10 bước", "13 bước", "3 bước"], "correct": 0},
    {"content": "🚦 Nếu đèn 🟢 xanh thì đi, 🔴 đỏ thì dừng. Đây là loại tư duy gì?", "level": "medium", "category": "logic", "answers": ["Điều kiện (nếu-thì)", "Lặp vô hạn", "Ngẫu nhiên", "Vẽ hình"], "correct": 0},
    {"content": "🧠 Nhớ lại: Khối 'đợi 1 giây' có tác dụng gì?", "level": "medium", "category": "memory", "answers": ["Tạm dừng 1 giây rồi mới chạy tiếp", "Xóa nhân vật", "Tăng tốc độ", "Đổi màu ngay lập tức"], "correct": 0},
    {"content": "🎮 Trong game, khi chạm biên màn hình thì đổi hướng. Sự kiện nào dùng?", "level": "medium", "category": "problem_solving", "answers": ["Khi chạm cạnh", "Khi nhấn phím A", "Khi nhấn cờ xanh", "Khi nhận tin 1"], "correct": 0},
    {"content": "📐 Hình tam giác có bao nhiêu góc?", "level": "medium", "category": "math", "answers": ["3 góc", "4 góc", "5 góc", "6 góc"], "correct": 0},
    {"content": "🔍 Trong Scratch, khối màu 🟡 vàng thường là loại khối gì?", "level": "medium", "category": "observation", "answers": ["Sự kiện (bắt đầu chương trình)", "Chuyển động", "Âm thanh", "Biến số"], "correct": 0},
    {"content": "🍎 Có 10 quả táo, cho bạn 3 quả. Còn lại mấy quả?", "level": "medium", "category": "math", "answers": ["7 quả", "3 quả", "10 quả", "13 quả"], "correct": 0},
    {"content": "🔄 Để mèo quay vòng tròn, cách nào hợp lý nhất?", "level": "medium", "category": "algorithm", "answers": ["Lặp: xoay một chút rồi di chuyển", "Chỉ di chuyển 1 lần", "Ẩn mèo", "Đổi tên dự án"], "correct": 0},
    {"content": "💡 Muốn 2 nhân vật nói chuyện với nhau, con cần dùng?", "level": "medium", "category": "problem_solving", "answers": ["Khối 'nói' và 'đợi'", "Khối 'xóa'", "Khối 'dừng tất cả'", "Khối 'ẩn'"], "correct": 0},
    {"content": "🎲 Biến 'điểm' ban đầu = 5. Cộng thêm 3 thì điểm mới là?", "level": "hard", "category": "math", "answers": ["8 điểm", "5 điểm", "3 điểm", "2 điểm"], "correct": 0},
    {"content": "🧩 Nếu số A lớn hơn 10 thì nói 'Lớn', ngược lại nói 'Nhỏ'. A = 8 thì nói gì?", "level": "hard", "category": "logic", "answers": ["Nhỏ", "Lớn", "Không nói gì", "Dừng chương trình"], "correct": 0},
    {"content": "🔢 Dãy số: 2, 4, 6, 8, ... Số tiếp theo là?", "level": "hard", "category": "algorithm", "answers": ["10", "9", "12", "7"], "correct": 0},
    {"content": "🎯 Trong game Scratch, mỗi lần nhấn phím Space nhân vật nhảy. Đây là sự kiện gì?", "level": "hard", "category": "observation", "answers": ["Khi phím Space được nhấn", "Khi cờ xanh được nhấn", "Khi chạm biên màn hình", "Khi hết thời gian"], "correct": 0},
    {"content": "🧠 Nhớ: Khối 'đặt biến điểm thành 0' dùng khi nào?", "level": "hard", "category": "memory", "answers": ["Khi bắt đầu game mới", "Khi kết thúc game", "Khi đổi nền", "Khi xóa nhân vật"], "correct": 0},
    {"content": "🔄 Lặp 5 lần, mỗi lần vẽ 1 hình vuông cạnh 20. Tổng cộng vẽ mấy hình?", "level": "hard", "category": "algorithm", "answers": ["5 hình", "20 hình", "1 hình", "4 hình"], "correct": 0},
    {"content": "🚗 Xe đi từ A → B → C. Muốn quay ngược về A, con cần?", "level": "hard", "category": "problem_solving", "answers": ["Đi ngược lại các bước", "Xóa xe", "Đổi màu xe", "Tắt màn hình"], "correct": 0},
    {"content": "📊 Biểu đồ có 4 cột ghi số: 3, 7, 5, 9. Cột nào cao nhất?", "level": "hard", "category": "observation", "answers": ["Cột 9", "Cột 3", "Cột 5", "Cột 7"], "correct": 0},
    {"content": "🎪 Mỗi câu trả lời đúng được +5 điểm. Trả lời đúng 3 câu thì được bao nhiêu điểm?", "level": "hard", "category": "math", "answers": ["15 điểm", "5 điểm", "10 điểm", "8 điểm"], "correct": 0},
    {"content": "🏆 Để tạo game hoàn chỉnh trên Scratch, bước cuối cùng thường là?", "level": "hard", "category": "sequencing", "answers": ["Kiểm tra và chạy thử game ▶️", "Xóa tất cả nhân vật", "Tắt âm thanh", "Đóng Scratch"], "correct": 0},
]

PYTHON_QUESTIONS = [
    {"content": "🐍 Python là ngôn ngữ lập trình. Biểu tượng Python là con gì?", "level": "easy", "category": "observation", "answers": ["Con rắn 🐍", "Con mèo 🐱", "Con chó 🐶", "Con chim 🐦"], "correct": 0},
    {"content": "💻 Lệnh `print('Xin chào')` trong Python dùng để làm gì?", "level": "easy", "category": "logic", "answers": ["In chữ ra màn hình", "Tắt máy tính", "Xóa file", "Đổi màu chữ"], "correct": 0},
    {"content": "🔢 Trong Python, 3 + 4 bằng bao nhiêu?", "level": "easy", "category": "math", "answers": ["7", "34", "12", "1"], "correct": 0},
    {"content": "📝 Biến số `tuoi = 10` nghĩa là gì?", "level": "easy", "category": "memory", "answers": ["Lưu giá trị 10 vào tên tuoi", "In ra số 10", "Xóa số 10", "Tắt chương trình"], "correct": 0},
    {"content": "🔤 Chuỗi ký tự trong Python đặt trong dấu gì?", "level": "easy", "category": "observation", "answers": ["Nháy đơn ' hoặc nháy kép \"", "Dấu ngoặc []", "Dấu ngoặc {}", "Không cần dấu gì"], "correct": 0},
    {"content": "➕ Phép tính 10 - 3 cho kết quả?", "level": "easy", "category": "math", "answers": ["7", "13", "3", "10"], "correct": 0},
    {"content": "🔄 Vòng lặp `for i in range(3)` sẽ chạy bao nhiêu lần?", "level": "easy", "category": "algorithm", "answers": ["3 lần", "1 lần", "0 lần", "5 lần"], "correct": 0},
    {"content": "📋 Thứ tự viết chương trình Python đúng:", "level": "easy", "category": "sequencing", "answers": ["Mở editor → Viết code → Chạy ▶️", "Chạy → Tắt máy → Viết code", "Xóa file → Chạy", "Tắt máy → Viết code"], "correct": 0},
    {"content": "❓ Dấu # trong Python dùng để làm gì?", "level": "easy", "category": "observation", "answers": ["Viết ghi chú (comment)", "In ra màn hình", "Tính toán", "Xóa code"], "correct": 0},
    {"content": "🎯 `if diem >= 5` trong Python nghĩa là kiểm tra điều gì?", "level": "easy", "category": "logic", "answers": ["Điểm có từ 5 trở lên không", "Điểm bằng 0", "In ra màn hình", "Xóa biến điểm"], "correct": 0},
    {"content": "🔢 6 × 2 trong Python cho kết quả?", "level": "medium", "category": "math", "answers": ["12", "62", "8", "36"], "correct": 0},
    {"content": "📦 List `[1, 2, 3]` có bao nhiêu phần tử?", "level": "medium", "category": "memory", "answers": ["3 phần tử", "1 phần tử", "2 phần tử", "6 phần tử"], "correct": 0},
    {"content": "🔄 `for i in range(1, 5)` sẽ lấy các số nào? (bắt đầu từ 1, dừng trước 5)", "level": "medium", "category": "algorithm", "answers": ["1, 2, 3, 4", "1, 2, 3, 4, 5", "0, 1, 2, 3, 4", "5, 4, 3, 2, 1"], "correct": 0},
    {"content": "🧩 `if x > 10: print('Lớn')` — x = 15 thì màn hình hiện gì?", "level": "medium", "category": "logic", "answers": ["Lớn", "Nhỏ", "15", "Không hiện gì"], "correct": 0},
    {"content": "🔍 `len('hello')` trả về bao nhiêu?", "level": "medium", "category": "observation", "answers": ["5", "4", "6", "0"], "correct": 0},
    {"content": "🍎 `tong = 5 + 3 * 2` — kết quả bằng bao nhiêu? (nhân trước, cộng sau)", "level": "medium", "category": "math", "answers": ["11", "16", "10", "13"], "correct": 0},
    {"content": "💡 Muốn nhập tên từ bàn phím, dùng hàm nào?", "level": "medium", "category": "problem_solving", "answers": ["input()", "print()", "len()", "range()"], "correct": 0},
    {"content": "🧠 Nhớ: Toán tử `==` dùng để?", "level": "medium", "category": "memory", "answers": ["So sánh bằng nhau", "Gán giá trị", "Cộng số", "In ra màn hình"], "correct": 0},
    {"content": "📐 Số chẵn tiếp theo sau 8 là?", "level": "medium", "category": "math", "answers": ["10", "9", "7", "12"], "correct": 0},
    {"content": "🔁 `while diem < 5: diem += 1` — ban đầu diem = 0, lặp mấy lần?", "level": "medium", "category": "algorithm", "answers": ["5 lần", "1 lần", "0 lần", "4 lần"], "correct": 0},
    {"content": "🔢 Dãy: 1, 3, 5, 7, ... Số tiếp theo?", "level": "hard", "category": "algorithm", "answers": ["9", "8", "10", "6"], "correct": 0},
    {"content": "🧩 `if diem >= 8: print('Giỏi')` — diem = 9 thì in ra gì?", "level": "hard", "category": "logic", "answers": ["Giỏi", "Giỏi lắm", "9", "Không in gì"], "correct": 0},
    {"content": "📊 `diem = [10, 20, 30]` — số ở giữa danh sách là?", "level": "hard", "category": "memory", "answers": ["20", "10", "30", "3"], "correct": 0},
    {"content": "🔢 20 + 20 + 20 + 20 bằng bao nhiêu?", "level": "hard", "category": "math", "answers": ["80", "60", "40", "100"], "correct": 0},
    {"content": "🔄 Viết `def chao():` trong Python để làm gì?", "level": "hard", "category": "observation", "answers": ["Tạo một hàm tên chao", "In ra chữ hello", "Xóa biến", "Tắt chương trình"], "correct": 0},
    {"content": "🔁 `for i in range(4): print(i)` — số lớn nhất được in ra là?", "level": "hard", "category": "problem_solving", "answers": ["3", "4", "0", "2"], "correct": 0},
    {"content": "🧠 `s = 'Python'` — chữ cái đầu tiên trong chuỗi là gì?", "level": "hard", "category": "memory", "answers": ["P", "h", "y", "n"], "correct": 0},
    {"content": "🎯 `if x % 2 == 0` dùng để kiểm tra số x là?", "level": "hard", "category": "logic", "answers": ["Số chẵn", "Số lẻ", "Số âm", "Số lớn hơn 10"], "correct": 0},
    {"content": "📈 1 + 2 + 3 + 4 bằng bao nhiêu?", "level": "hard", "category": "math", "answers": ["10", "4", "5", "8"], "correct": 0},
    {"content": "🏆 Sau khi viết xong code Python, bước quan trọng cuối là?", "level": "hard", "category": "sequencing", "answers": ["Chạy thử và kiểm tra kết quả ▶️", "Xóa toàn bộ code", "Tắt máy tính", "Đổi tên file"], "correct": 0},
]


def _validate_answers(answer_texts, content):
    normalized = [t.strip().lower() for t in answer_texts]
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"Đáp án trùng nhau trong câu: {content[:60]}...")
    if len(answer_texts) < 2:
        raise ValueError(f"Cần ít nhất 2 đáp án: {content[:60]}...")


def _validate_correct_index(answer_texts, correct_index, content):
    if correct_index < 0 or correct_index >= len(answer_texts):
        raise ValueError(
            f"Chỉ số đáp án đúng không hợp lệ ({correct_index}): {content[:60]}..."
        )


def _build_answers(answer_texts, correct_index, content=""):
    _validate_answers(answer_texts, content)
    _validate_correct_index(answer_texts, correct_index, content)
    items = [
        {"answer_text": text, "is_correct": i == correct_index}
        for i, text in enumerate(answer_texts)
    ]
    random.shuffle(items)
    correct_count = sum(1 for item in items if item.get("is_correct") is True)
    if correct_count != 1:
        raise ValueError(f"Phải có đúng 1 đáp án đúng, có {correct_count}: {content[:60]}...")
    for item in items:
        item["id"] = str(ObjectId())
    return items


def _add_questions(course_id, questions_data):
    docs = []
    for i, q in enumerate(questions_data):
        texts = q["answers"]
        if len(texts) != 4:
            raise ValueError(f"Câu {i + 1} cần đúng 4 đáp án: {q['content'][:50]}...")
        correct_idx = q.get("correct", 0)
        docs.append({
            "course_id": course_id,
            "content": q["content"],
            "image_url": q.get("image_url"),
            "level": q["level"],
            "category": q["category"],
            "order_num": i + 1,
            "answers": _build_answers(texts, correct_idx, q["content"]),
        })
    if docs:
        col("questions").insert_many(docs)


def seed_database():
    if col("courses").find_one():
        return

    scratch_result = col("courses").insert_one({
        "name": "Scratch",
        "slug": "scratch",
        "description": "Dành cho học sinh mới bắt đầu - lập trình kéo thả với chú mèo Scratch.",
    })
    python_result = col("courses").insert_one({
        "name": "Python",
        "slug": "python",
        "description": "Dành cho học sinh yêu thích tư duy logic - ngôn ngữ lập trình Python.",
    })

    scratch_id = oid_str(scratch_result.inserted_id)
    python_id = oid_str(python_result.inserted_id)

    _add_questions(scratch_id, SCRATCH_QUESTIONS)
    _add_questions(python_id, PYTHON_QUESTIONS)

    col("users").insert_one({
        "full_name": "Admin",
        "email": "admin@kiemtra.edu.vn",
        "password_hash": hash_password("admin123"),
        "role": "admin",
        "created_at": datetime.utcnow(),
    })

    col("users").create_index("email", unique=True)
    col("courses").create_index("slug", unique=True)
    col("questions").create_index([("course_id", 1), ("order_num", 1)])
    col("tests").create_index("submitted_at")

    print("Seed MongoDB hoan tat!")
