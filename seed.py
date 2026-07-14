from datetime import datetime
import random
from bson import ObjectId
from database import col, oid_str
from models import hash_password

SCRATCH_QUESTIONS = [
    # --- Kiến thức Scratch cơ bản (16) ---
    {"content": "▶️ Để chạy chương trình Scratch, ghép khối vào sự kiện nào?", "level": "medium", "category": "sequencing", "answers": ["Khi bấm cờ xanh ▶️", "Khi bấm cờ đỏ ⏹️", "Khi nhấn Delete", "Khi tắt máy"], "correct": 0},
    {"content": "🟦 Khối màu xanh dương thuộc nhóm lệnh gì?", "level": "medium", "category": "observation", "answers": ["Chuyển động (Motion)", "Sự kiện (Events)", "Âm thanh", "Biến số"], "correct": 0},
    {"content": "🐱 Muốn mèo đi thẳng 50 bước, dùng khối nào?", "level": "medium", "category": "problem_solving", "answers": ["Di chuyển 50 bước", "Xoay 50 độ", "Đổi kích thước 50%", "Ẩn nhân vật"], "correct": 0},
    {"content": "⬆️ Muốn nhân vật nhảy lên, thay đổi tọa độ nào?", "level": "medium", "category": "problem_solving", "answers": ["Tăng y", "Giảm x", "Đổi hướng 0°", "Ẩn nhân vật"], "correct": 0},
    {"content": "📍 Khối 'đi tới x: 0 y: 0' đưa nhân vật về đâu?", "level": "medium", "category": "problem_solving", "answers": ["Tâm màn hình", "Góc trên phải", "Ra ngoài màn hình", "Vị trí ngẫu nhiên"], "correct": 0},
    {"content": "🏃 Mèo Scratch làm lần lượt:\n\n① Xoay 90°\n② Di chuyển 10 bước\n③ Nói \"Xong!\"\n\nSau khi đi thẳng xong, mèo làm gì tiếp theo?", "level": "medium", "category": "sequencing", "answers": ["Nói \"Xong!\"", "Xoay 90°", "Di chuyển 10 bước", "Ẩn đi"], "correct": 0},
    {"content": "🔁 Chương trình Scratch:\n\n• Lặp 3 lần\n• Mỗi lần lặp: di chuyển 4 bước\n\nTổng cộng mèo đi được bao nhiêu bước?", "level": "medium", "category": "algorithm", "answers": ["12 bước", "7 bước", "4 bước", "3 bước"], "correct": 0},
    {"content": "🔄 Vẽ hình vuông cạnh 50:\n\n• Lặp 4 lần\n• Mỗi lần: di chuyển 50 bước → xoay 90°\n\nTổng quãng đường mèo đi?", "level": "medium", "category": "math", "answers": ["200 bước", "50 bước", "150 bước", "100 bước"], "correct": 0},
    {"content": "🧱 Chạm cạnh màn hình thì quay ngược — dùng khối nào?", "level": "medium", "category": "problem_solving", "answers": ["Nếu chạm cạnh thì quay lại", "Lặp vô hạn", "Đổi nền", "Dừng tất cả"], "correct": 0},
    {"content": "💬 Hai nhân vật nói nối tiếp — dùng khối nào?", "level": "medium", "category": "problem_solving", "answers": ["Nói ... và đợi", "Ẩn và hiện", "Xóa bản sao", "Dừng khối khác"], "correct": 0},
    {"content": "🔄 Vẽ hình tròn bằng mèo — cách phổ biến?", "level": "medium", "category": "algorithm", "answers": ["Lặp: xoay một chút + di chuyển", "Di chuyển 1 lần", "Ẩn mèo", "Đổi tên dự án"], "correct": 0},
    {"content": "♾️ 'Lặp mãi mãi' khác 'lặp 10 lần' ở điểm nào?", "level": "medium", "category": "logic", "answers": ["Lặp không dừng cho đến khi dừng chương trình", "Chỉ chạy 1 lần", "Chỉ khi cờ đỏ", "Không lặp được"], "correct": 0},
    {"content": "📣 Khối 'phát tin' (broadcast) dùng để?", "level": "medium", "category": "problem_solving", "answers": ["Báo sự kiện cho nhân vật khác", "In chữ ra màn hình", "Lưu file", "Tắt Scratch"], "correct": 0},
    {"content": "🎭 Đổi trang phục (costume) nhân vật — khối nào?", "level": "medium", "category": "sequencing", "answers": ["Chuyển sang trang phục tiếp theo", "Đổi nền trắng", "Xóa biến", "Dừng âm thanh"], "correct": 0},
    {"content": "🚦 Đèn xanh thì đi, đỏ thì dừng — tư duy lập trình gì?", "level": "medium", "category": "logic", "answers": ["Điều kiện (nếu — thì)", "Lặp vô hạn", "Ngẫu nhiên", "Vẽ hình"], "correct": 0},
    {"content": "🔁 Lặp 'di chuyển 8 bước' 4 lần — tổng bao nhiêu bước?", "level": "medium", "category": "math", "answers": ["32 bước", "8 bước", "12 bước", "4 bước"], "correct": 0},
    # --- Tình huống game (3) — tính điểm / biến ---
    {"content": "🎮 Trò chơi bắt sao:\n\n• Điểm ban đầu = 5\n• Mỗi lần chạm sao: +2 điểm\n• Bạn chạm sao 3 lần\n\nĐiểm cuối cùng là bao nhiêu?", "level": "medium", "category": "math", "answers": ["11 điểm", "5 điểm", "6 điểm", "8 điểm"], "correct": 0},
    {"content": "🎮 Game né vật cản:\n\n• Điểm ban đầu = 20\n• Chạm vật cản 3 lần\n• Mỗi lần chạm: trừ 5 điểm\n\nĐiểm còn lại?", "level": "medium", "category": "math", "answers": ["5 điểm", "10 điểm", "15 điểm", "0 điểm"], "correct": 0},
    {"content": "⭐ Biến \"sao\" = 0\n\nLặp 4 lần, mỗi lần:\n→ Đổi \"sao\" thêm 1\n\nSau khi chạy xong, sao bằng bao nhiêu?", "level": "medium", "category": "math", "answers": ["4", "0", "1", "3"], "correct": 0},
    # --- Khó cuối đề (10) — phân loại học sinh ---
    {"content": "🔁 Lặp 5 lần, MỖI lần lặp 'di chuyển 2 bước' 4 lần — tổng bao nhiêu bước?", "level": "hard", "category": "algorithm", "answers": ["40 bước", "20 bước", "9 bước", "10 bước"], "correct": 0},
    {"content": "👥 Tạo 3 bản sao (clone) + 1 nhân vật gốc — có tất cả mấy nhân vật?", "level": "hard", "category": "problem_solving", "answers": ["4 nhân vật", "3 nhân vật", "1 nhân vật", "7 nhân vật"], "correct": 0},
    {"content": "📨 Muốn nhân vật B chạy khi nhân vật A 'phát tin bắt đầu', B cần khối nào?", "level": "hard", "category": "sequencing", "answers": ["Khi nhận tin bắt đầu", "Khi bấm cờ xanh", "Khi chạm biên", "Khi ẩn"], "correct": 0},
    {"content": "🔄 Xoay 15° rồi lặp 24 lần — mèo quay được mấy vòng tròn?", "level": "hard", "category": "algorithm", "answers": ["1 vòng (360°)", "2 vòng", "Nửa vòng", "Không quay"], "correct": 0},
    {"content": "🎨 Nếu 'chạm màu đỏ' thì dừng lại — cần khối nhóm nào?", "level": "hard", "category": "observation", "answers": ["Nhận biết (Sensing) + Điều kiện", "Chỉ Âm thanh", "Chỉ Vẽ", "Chỉ Biến"], "correct": 0},
    {"content": "🧩 Thứ tự đúng: đặt điểm = 0 → lặp 10 lần chơi → nếu chạm sao thì +1 điểm.\n\nBước đầu tiên là gì?", "level": "hard", "category": "sequencing", "answers": ["Đặt điểm = 0", "Lặp 10 lần", "Chạm sao +1", "Nói Thắng"], "correct": 0},
    {"content": "🎯 Một nhân vật nhận được tin nhắn \"Bắt đầu\" rồi chạy chương trình riêng của nó.\n\nĐây là ví dụ của:", "level": "hard", "category": "problem_solving", "answers": ["Sự kiện và truyền tin nhắn", "Biến", "Điều kiện", "Tọa độ"], "correct": 0},
    {"content": "📍 Nhân vật đang ở tọa độ (0, 0).\n\nSau đó:\n• thay đổi x thêm 50\n• thay đổi y thêm 100\n\nNhân vật ở tọa độ nào?", "level": "hard", "category": "problem_solving", "answers": ["(50, 100)", "(100, 50)", "(50, 50)", "(100, 100)"], "correct": 0},
    {"content": "🎯 Để thắng game:\n\n• Phải chạm sao\n• VÀ điểm > 5\n\n• Điểm hiện tại = 8\n• Vừa chạm sao\n\nBạn có thắng không?", "level": "hard", "category": "logic", "answers": ["Có, thắng", "Không, chưa đủ", "Chỉ cần chạm sao", "Chỉ cần điểm > 5"], "correct": 0},
    {"content": "👥 Ban đầu có 1 nhân vật.\nLặp 2 lần, mỗi lần tạo 1 bản sao (clone).\n\nSau khi chạy xong có tất cả mấy nhân vật?", "level": "hard", "category": "problem_solving", "answers": ["3 nhân vật", "2 nhân vật", "1 nhân vật", "4 nhân vật"], "correct": 0},
    {"content": "📐 Sắp xếp các khối để mèo vẽ hình tam giác:\n\n① Xoay 120 độ\n② Di chuyển 100 bước\n③ Lặp lại 3 lần\n\nThứ tự đúng là?", "image_url": "/images/scratch/triangle-blocks-hint.svg", "level": "hard", "category": "sequencing", "answers": ["Lặp lại 3 lần\n    Di chuyển 100 bước\n    Xoay 120 độ", "Di chuyển 100 bước\nLặp lại 3 lần\n    Xoay 120 độ", "Lặp lại 3 lần\n    Xoay 120 độ\n    Di chuyển 100 bước", "Xoay 120 độ\nDi chuyển 100 bước"], "correct": 0},
]

PYTHON_QUESTIONS = [
    # --- Trung bình (8) — đọc code, suy luận từng bước ---
    {"content": "`print('2' + '3')`\nKết quả?", "level": "medium", "category": "logic", "answers": ["23", "5", "6", "2 + 3"], "correct": 0},
    {"content": "`ds = [5, 10, 15]`\n`print(len(ds))`\nIn ra?", "level": "medium", "category": "memory", "answers": ["3", "5", "15", "1"], "correct": 0},
    {"content": "`n = 0`\n`while n < 3:`\n`    n += 1`\nVòng lặp chạy mấy lần?", "level": "medium", "category": "algorithm", "answers": ["3 lần", "0 lần", "2 lần", "4 lần"], "correct": 0},
    {"content": "`s = 'hello'`\n`print(s[0])`\nIn ra?", "level": "medium", "category": "memory", "answers": ["h", "e", "o", "hello"], "correct": 0},
    {"content": "`diem = [12, 20, 8]`\n`print(diem[1])`\nIn ra?", "level": "medium", "category": "memory", "answers": ["20", "12", "8", "1"], "correct": 0},
    {"content": "`x = 14`\n`if x % 2 == 0:`\n`    print('Chẵn')`\nIn ra?", "level": "medium", "category": "logic", "answers": ["Chẵn", "Lẻ", "14", "0"], "correct": 0},
    {"content": "`def chao():`\n`    print('Hi')`\n`chao()`\nIn ra?", "level": "medium", "category": "problem_solving", "answers": ["Hi", "chao", "def chao", "Không in gì"], "correct": 0},
    {"content": "`print(7 == 7)`\nKết quả?", "level": "medium", "category": "logic", "answers": ["True", "False", "7", "0"], "correct": 0},
    # --- Khó (18) — đọc code, suy nghĩ sâu ---
    {"content": "`x = [1, 2, 3]`\n`y = x`\n`y.append(4)`\n`print(x)`\nIn ra?", "level": "hard", "category": "memory", "answers": ["[1, 2, 3, 4]", "[1, 2, 3]", "[4]", "[1, 2, 3, 4, 4]"], "correct": 0},
    {"content": "`x = [1, 2, 3]`\n`y = x[:]`\n`y.append(4)`\n`print(x)`\nIn ra?", "level": "hard", "category": "memory", "answers": ["[1, 2, 3]", "[1, 2, 3, 4]", "[4]", "Lỗi"], "correct": 0},
    {"content": "`a = [1, 2]`\n`b = a + [3]`\n`print(a)`\nIn ra?", "level": "hard", "category": "memory", "answers": ["[1, 2]", "[1, 2, 3]", "[3]", "[1, 3]"], "correct": 0},
    {"content": "`nums = [10, 20, 30]`\n`nums[1] = 99`\n`print(nums)`\nIn ra?", "level": "hard", "category": "memory", "answers": ["[10, 99, 30]", "[10, 20, 30]", "[99]", "[20, 99]"], "correct": 0},
    {"content": "`tong = 0`\n`for i in [1, 2, 3]:`\n`    if i == 2:`\n`        continue`\n`    tong += i`\n`print(tong)`\nKết quả?", "level": "hard", "category": "algorithm", "answers": ["4", "6", "2", "3"], "correct": 0},
    {"content": "`dem = 0`\n`for ch in 'aaa':`\n`    if ch == 'a':`\n`        dem += 1`\n`print(dem)`\nKết quả?", "level": "hard", "category": "algorithm", "answers": ["3", "1", "0", "aaa"], "correct": 0},
    {"content": "`kq = ''`\n`for i in range(3):`\n`    kq += str(i)`\n`print(kq)`\nIn ra?", "level": "hard", "category": "algorithm", "answers": ["012", "123", "0 1 2", "6"], "correct": 0},
    {"content": "`x = '5'`\n`print(int(x) + 3)`\nKết quả?", "level": "hard", "category": "logic", "answers": ["8", "53", "5", "'8'"], "correct": 0},
    {"content": "`diem = 85`\n`if diem >= 90:`\n`    print('A')`\n`elif diem >= 70:`\n`    print('B')`\n`else:`\n`    print('C')`\nIn ra?", "level": "hard", "category": "logic", "answers": ["B", "A", "C", "85"], "correct": 0},
    {"content": "`for i in range(2):`\n`    for j in range(3):`\n`        print('*')`\nIn bao nhiêu dòng * ?", "level": "hard", "category": "algorithm", "answers": ["6 dòng", "5 dòng", "3 dòng", "2 dòng"], "correct": 0},
    {"content": "`s = 'Python'`\n`print(s[1:4])`\nIn ra?", "level": "hard", "category": "memory", "answers": ["yth", "Pyt", "ytho", "hon"], "correct": 0},
    {"content": "`def nhan_doi(x):`\n`    return x * 2`\n`print(nhan_doi(4))`\nKết quả?", "level": "hard", "category": "problem_solving", "answers": ["8", "4", "2", "nhan_doi(4)"], "correct": 0},
    {"content": "`for i in range(1, 10):`\n`    if i % 2 == 0:`\n`        print(i)`\nSố chẵn lớn nhất được in?", "level": "hard", "category": "algorithm", "answers": ["8", "9", "6", "10"], "correct": 0},
    {"content": "`x = 1`\n`for _ in range(4):`\n`    x *= 2`\n`print(x)`\nGiá trị cuối?", "level": "hard", "category": "algorithm", "answers": ["16", "8", "4", "2"], "correct": 0},
    {"content": "`tong = 0`\n`for i in range(1, 6):`\n`    tong += i`\n`print(tong)`\nKết quả?", "level": "hard", "category": "math", "answers": ["15", "5", "10", "6"], "correct": 0},
    {"content": "`n = 5`\n`while n > 0:`\n`    n -= 1`\nVòng lặp chạy mấy lần?", "level": "hard", "category": "algorithm", "answers": ["5 lần", "4 lần", "6 lần", "0 lần"], "correct": 0},
    {"content": "`lst = [2, 4, 6]`\n`print(lst[0] + lst[2])`\nKết quả?", "level": "hard", "category": "math", "answers": ["8", "6", "4", "10"], "correct": 0},
    {"content": "`a, b = 3, 5`\n`print(a < b and b < 10)`\nIn ra?", "level": "hard", "category": "logic", "answers": ["True", "False", "5", "3"], "correct": 0},
    # --- Khó cuối đề (4) — phân loại học sinh ---
    {"content": "Kết quả của chương trình sau là gì?\n\n`total = 0`\n`for i in range(1, 6):`\n`    if i % 2 == 0:`\n`        total += i`\n`    else:`\n`        total -= i`\n`print(total)`", "level": "hard", "category": "algorithm", "answers": ["-3", "3", "-5", "5"], "correct": 0},
    {"content": "Kết quả của chương trình sau là gì?\n\n`numbers = [3, 6, 9, 12, 15]`\n`count = 0`\n`for num in numbers:`\n`    if num % 3 == 0 and num % 2 == 0:`\n`        count += 1`\n`print(count)`", "level": "hard", "category": "algorithm", "answers": ["2", "3", "4", "5"], "correct": 0},
    {"content": "Kết quả của chương trình sau là gì?\n\n`nums = [1, 2, 3, 4]`\n`for i in range(len(nums)):`\n`    nums[i] *= 2`\n`print(nums)`", "level": "hard", "category": "memory", "answers": ["[1, 2, 3, 4]", "[2, 4, 6, 8]", "[1, 4, 9, 16]", "Lỗi"], "correct": 1},
    {"content": "Kết quả là gì?\n\n`a = [1, 2, 3]`\n`b = a`\n`a = [4, 5]`\n`print(b)`", "level": "hard", "category": "memory", "answers": ["[4, 5]", "[1, 2, 3]", "[]", "Lỗi"], "correct": 1},
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
