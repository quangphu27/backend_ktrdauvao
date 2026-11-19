"""Cập nhật «Bài kiểm tra Scratch giữa khóa»: giữ 8 câu cũ + thêm 21 câu TN/TL (+ 5 lab).

Mix TN + TL · khó · một số câu có bẫy (hướng Scratch, đặt/thay đổi biến, phát tin…).
Slug cố định: scratch-giua-khoa
"""

from datetime import datetime
import re

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import quiz_to_dict, sanitize_questions, new_id

QUIZ_TITLE = "Bài kiểm tra Scratch giữa khóa"
FIXED_SLUG = "scratch-giua-khoa"
OLD_SLUG = "u5s0wv7i"


def _strip_cau(content):
    return re.sub(r"^Câu\s*\d+\s*:\s*", "", (content or "").strip(), flags=re.IGNORECASE)


def mcq(content, options, correct, points=1, explanation=None):
    """options: list[str]; correct: index 0-based."""
    return {
        "type": "mcq",
        "content": content,
        "points": points,
        "options": [
            {"text": t, "is_correct": (i == correct)}
            for i, t in enumerate(options)
        ],
        "explanation": explanation,
    }


def text(content, correct_answer, aliases=None, points=1):
    return {
        "type": "text",
        "content": content,
        "points": points,
        "correct_answer": str(correct_answer),
        "answer_aliases": list(aliases or []),
    }


# 17 câu mới (khó / có bẫy)
NEW_QUESTIONS = [
    # --- Vẽ hình vuông / tròn ---
    mcq(
        "Muốn vẽ hình vuông cạnh 80 bước, khối lệnh nào đúng nhất?",
        [
            "Lặp 4 lần: di chuyển 80 bước, xoay phải 90 độ (bút đang đặt xuống)",
            "Lặp 360 lần: di chuyển 80 bước, xoay phải 1 độ",
            "Lặp 4 lần: di chuyển 80 bước, xoay phải 45 độ",
            "Di chuyển 80 bước rồi xoay phải 360 độ một lần",
        ],
        0,
        explanation="Hình vuông: 4 cạnh, mỗi góc ngoài 90°. Xoay 45° sẽ ra hình sao/chéo, không phải vuông.",
    ),
    mcq(
        "Vẽ hình tròn bán kính R bằng cách lặp 360 lần: mỗi lần xoay phải 1 độ. Mỗi lần nên di chuyển bao nhiêu bước?",
        [
            "2 × π × R / 360  (chu vi chia 360)",
            "R / 360",
            "2 × R  (đường kính)",
            "π × R  (nửa chu vi)",
        ],
        0,
        explanation="Chu vi = 2πR; chia đều 360 bước nhỏ ≈ cung tròn.",
    ),
    mcq(
        "Em quên khối «đặt bút xuống» rồi chạy chương trình vẽ hình vuông. Kết quả nào đúng?",
        [
            "Nhân vật vẫn di chuyển đúng quỹ đạo nhưng không thấy nét vẽ",
            "Hình vuông vẫn hiện rõ trên sân khấu",
            "Scratch báo lỗi và dừng chương trình",
            "Tự động đặt bút xuống sau lần xoay đầu tiên",
        ],
        0,
    ),
    text(
        "Muốn vẽ ngũ giác đều (5 cạnh), mỗi lần xoay phải bao nhiêu độ? (chỉ ghi số)",
        "72",
        aliases=["72 độ", "72°", "xoay 72", "xoay phải 72"],
    ),
    # --- x, y ---
    mcq(
        "Nhân vật ở (x=10, y=20). Chạy: thay đổi x đi 5; thay đổi y đi -8. Tọa độ mới là?",
        [
            "x=15, y=12",
            "x=5, y=28",
            "x=15, y=28",
            "x=10, y=12",
        ],
        0,
        explanation="Bẫy: nhầm dấu y hoặc quên chỉ một trong hai tọa độ thay đổi.",
    ),
    mcq(
        "Muốn nhân vật đi sang TRÁI 15 bước mà KHÔNG đổi hướng đang nhìn, dùng khối nào?",
        [
            "Thay đổi x đi -15",
            "Thay đổi y đi -15",
            "Di chuyển 15 bước",
            "Đặt hướng 180 rồi di chuyển 15 bước",
        ],
        0,
        explanation="«Di chuyển» đi theo hướng hiện tại — không phải lúc nào cũng sang trái. Đổi x âm = trái trên sân khấu.",
    ),
    mcq(
        "Khối «đi tới x: 0 y: 0» khác gì «thay đổi x đi 0; thay đổi y đi 0»?",
        [
            "Đi tới đặt tuyệt đối về gốc; thay đổi 0 gần như không đổi vị trí hiện tại",
            "Hai khối luôn cho kết quả giống hệt nhau",
            "Thay đổi 0 sẽ đưa nhân vật về (0,0)",
            "Đi tới chỉ đổi x, không đổi y",
        ],
        0,
    ),
    text(
        "Nhân vật ở x=−40, y=25. Lặp 3 lần «thay đổi x đi 10». Sau đó y bằng bao nhiêu? (chỉ ghi số)",
        "25",
        aliases=["y=25", "y = 25"],
    ),
    # --- Hướng (bẫy cổ điển Scratch: 0 = lên) ---
    mcq(
        "Trong Scratch, hướng 0 độ nghĩa là nhân vật đang nhìn về phía nào?",
        [
            "Lên trên (phía y dương)",
            "Sang phải (phía x dương)",
            "Xuống dưới",
            "Sang trái",
        ],
        0,
        explanation="BẪY: nhiều bạn nhầm 0° = phải như toán/hình học. Scratch: 0 = lên, 90 = phải, −90 = trái, 180 = xuống.",
    ),
    mcq(
        "Nhân vật đang hướng 90° (nhìn phải). Chạy «xoay phải 90 độ». Hướng mới là?",
        [
            "180° (nhìn xuống)",
            "0° (nhìn lên)",
            "90° (vẫn nhìn phải)",
            "−90° (nhìn trái)",
        ],
        0,
    ),
    mcq(
        "Muốn nhân vật luôn quay mặt về phía con trỏ chuột mỗi khung hình, khối nào phù hợp trong «lặp lại mãi»?",
        [
            "Hướng về phía con trỏ chuột",
            "Đặt hướng 90",
            "Xoay phải 15 độ",
            "Đi tới x: chuột y: chuột một lần rồi dừng",
        ],
        0,
    ),
    text(
        "Nhân vật bắt đầu hướng 0°. Chạy lần lượt: xoay phải 90°; xoay phải 90°; xoay trái 90°. Hướng cuối cùng là bao nhiêu độ? (chỉ ghi số, có thể kèm °)",
        "90",
        aliases=["90°", "90 độ", "hướng 90"],
    ),
    # --- Phát tin ---
    mcq(
        "Nhân vật A phát tin «nổ». Nhân vật B có script «Khi nhận được tin nổ → ẩn». Điều nào đúng?",
        [
            "Chỉ B (và mọi nhân vật có «khi nhận được tin nổ») phản ứng; A không tự ẩn nếu A không có script đó",
            "Mọi nhân vật trên sân khấu đều tự ẩn ngay",
            "Chỉ A ẩn vì A là người phát tin",
            "Tin chỉ hoạt động nếu A và B cùng một trang phục",
        ],
        0,
    ),
    # --- Biến ---
    mcq(
        "Biến «điểm» đang = 7. Chạy «đặt điểm thành 1» rồi «thay đổi điểm đi 1». Giá trị cuối?",
        [
            "2",
            "8",
            "1",
            "9",
        ],
        0,
        explanation="BẪY: nhầm «đặt thành 1» với «thay đổi đi 1» → nhiều bạn chọn 8.",
    ),
    mcq(
        "Biến «mạng» tạo «Cho tất cả nhân vật». Nhân vật A đặt mạng thành 3. Nhân vật B đọc mạng được giá trị nào?",
        [
            "3 (cùng một biến dùng chung)",
            "0 vì mỗi nhân vật có bản sao riêng",
            "Không đọc được biến của A",
            "Luôn bằng số lượng nhân vật trên sân khấu",
        ],
        0,
    ),
    text(
        "Biến «mạng» = 3. Mỗi lần chạm gai: thay đổi mạng đi −1. Sau đúng 2 lần chạm gai (không hồi mạng), mạng bằng bao nhiêu?",
        "1",
        aliases=["mạng = 1", "mang = 1", "1 mạng"],
    ),
    # --- Khối / điều khiển / bẫy ---
    mcq(
        "Khối nào DỪNG toàn bộ chương trình (mọi nhân vật), không chỉ script hiện tại?",
        [
            "Dừng tất cả",
            "Dừng script này",
            "Xóa bản sao này",
            "Ẩn",
        ],
        0,
    ),
]


def load_existing_eight(quiz_doc):
    """Giữ nguyên 8 câu cũ (kèm id). Idempotent khi seed lại 30 câu."""
    old = list(quiz_doc.get("questions") or [])
    if len(old) < 8:
        raise RuntimeError(f"Quiz chỉ có {len(old)} câu, kỳ vọng ≥ 8 câu gốc.")
    marker = "Vẽ hình tròn trong Scratch, di chuyển 1 bước"
    for i, q in enumerate(old):
        if marker in _strip_cau(q.get("content") or ""):
            chunk = old[i : i + 8]
            if len(chunk) == 8:
                return chunk
    return old[:8]


SCRATCH_LAB_QUESTIONS = [
    {
        "type": "scratch_blocks",
        "lab_slug": "ve-hinh-vuong",
        "content": "Làm trên web: Vẽ hình vuông cạnh 100.",
        "points": 2,
        "hint": None,
    },
]


def build_all_questions(existing_eight):
    preserved = []
    for i, q in enumerate(existing_eight):
        raw = {
            "id": q.get("id") or new_id(),
            "type": q.get("type") or "mcq",
            "content": _strip_cau(q.get("content") or ""),
            "image_url": q.get("image_url"),
            "points": int(q.get("points") or 1),
            "order_num": i,
            "options": q.get("options") or [],
            "correct_answer": q.get("correct_answer"),
            "answer_aliases": q.get("answer_aliases") or [],
            "explanation": q.get("explanation"),
        }
        preserved.append(raw)

    combined = preserved + NEW_QUESTIONS + SCRATCH_LAB_QUESTIONS
    assert len(NEW_QUESTIONS) == 17, len(NEW_QUESTIONS)
    assert len(SCRATCH_LAB_QUESTIONS) == 1, len(SCRATCH_LAB_QUESTIONS)
    assert len(combined) == 26, len(combined)

    questions = sanitize_questions(combined)
    for i, q in enumerate(questions):
        q["order_num"] = i
        q["content"] = f"Câu {i + 1}: {_strip_cau(q['content'])}"
    return questions


def main():
    app = create_app()
    with app.app_context():
        existing = (
            col("quizzes").find_one({"title": QUIZ_TITLE})
            or col("quizzes").find_one({"slug": FIXED_SLUG})
            or col("quizzes").find_one({"slug": OLD_SLUG})
        )
        if not existing:
            raise SystemExit(
                "Không tìm thấy quiz «Bài kiểm tra Scratch giữa khóa». "
                "Hãy tạo quiz 8 câu trước hoặc kiểm tra Mongo."
            )

        eight = load_existing_eight(existing)
        questions = build_all_questions(eight)

        description = (
            "Kiểm tra giữa khóa Scratch — 25 câu TN/TL + 1 bài Scratch làm trực tiếp trên web "
            "(vẽ hình vuông). Thời gian 60 phút."
        )
        now = datetime.utcnow()
        col("quizzes").update_one(
            {"_id": existing["_id"]},
            {
                "$set": {
                    "title": QUIZ_TITLE,
                    "slug": FIXED_SLUG,
                    "description": description,
                    "duration_minutes": 60,
                    "is_active": True,
                    "questions": questions,
                    "updated_at": now,
                }
            },
        )
        existing.update(
            {
                "title": QUIZ_TITLE,
                "slug": FIXED_SLUG,
                "description": description,
                "questions": questions,
            }
        )
        data = quiz_to_dict(existing, include_answers=True)
        mc = sum(1 for q in data["questions"] if q.get("type") == "mcq")
        tl = sum(1 for q in data["questions"] if q.get("type") == "text")
        sb = sum(1 for q in data["questions"] if q.get("type") == "scratch_blocks")
        pts = sum(int(q.get("points") or 0) for q in data["questions"])
        print("UPDATED")
        print(f"id={data['id']}")
        print(f"slug={data['slug']}")
        print(f"questions={len(data['questions'])} mcq={mc} text={tl} scratch_blocks={sb} points={pts}")
        print(f"public=/quiz/{data['slug']}")
        print(f"labs=/scratch")
        print(f"edit=/admin/quizzes/{data['id']}/edit")


if __name__ == "__main__":
    main()
