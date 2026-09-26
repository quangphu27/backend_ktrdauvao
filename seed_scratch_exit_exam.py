"""Seed: Kiểm tra đầu ra Scratch

- 14 câu TN mới (user gửi)
- 16 câu TN lấy từ ngân hàng questions Scratch có sẵn
- Xáo trộn vị trí 30 câu TN
- 1 câu tự luận nộp .sb3 (40%)

Điểm: 30 TN × 2 = 60 (60%) + tự luận 40 = 100.
Đồng thời đảm bảo 14 câu mới (+ 2 bổ sung) có trong /admin/questions Scratch.
"""

from datetime import datetime
import random
import re

from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col, oid_str
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions, new_id

QUIZ_TITLE = "Kiểm tra đầu ra Scratch"
FIXED_SLUG = "scratch-dau-ra"
BANK_TAG = "scratch_exit"
MCQ_POINTS = 2  # 30 × 2 = 60 → 60%
ESSAY_POINTS = 40  # 40%
BANK_PICK = 16
NEW_COUNT = 14


def _strip_cau_prefix(content):
    return re.sub(r"^Câu\s*\d+\s*:\s*", "", (content or "").strip(), flags=re.IGNORECASE)


# 14 câu mới do user gửi
NEW_QUESTIONS = [
    {
        "content": "Trong trò chơi Mèo bắt chuột, con chuột di chuyển theo đối tượng nào?",
        "options": ["Con mèo", "Con trỏ chuột", "Cạnh sân khấu", "Bàn phím"],
        "correct": 1,
        "level": "easy",
        "category": "observation",
    },
    {
        "content": "Trong trò chơi Mèo bắt chuột, con mèo di chuyển theo đối tượng nào?",
        "options": ["Con chuột", "Con trỏ chuột", "Cạnh sân khấu", "Bàn phím"],
        "correct": 0,
        "level": "easy",
        "category": "observation",
    },
    {
        "content": (
            "Muốn vẽ hình tròn, cho nhân vật di chuyển 1 bước, xoay 1 độ. "
            "Hành động này cần lặp lại bao nhiêu lần?"
        ),
        "options": ["90 lần", "180 lần", "360 lần", "720 lần"],
        "correct": 2,
        "level": "medium",
        "category": "algorithm",
    },
    {
        "content": (
            "Muốn vẽ bông hoa 8 cánh, biết rằng đã có chương trình vẽ 1 cánh. "
            "Cần lặp lại hành động vẽ bao nhiêu lần?"
        ),
        "options": ["4 lần", "6 lần", "8 lần", "16 lần"],
        "correct": 2,
        "level": "medium",
        "category": "algorithm",
    },
    {
        "content": (
            "Trong trò chơi Cá lớn nuốt cá bé, cá bé di chuyển trái phải và khi chạm cạnh "
            "thì bật lại. Dùng khối lệnh nào?"
        ),
        "options": [
            "Di chuyển 10 bước",
            "Xoay 15 độ",
            "Bật lại nếu chạm cạnh",
            "Đi tới con trỏ chuột",
        ],
        "correct": 2,
        "level": "medium",
        "category": "problem_solving",
    },
    {
        "content": (
            "Trong trò chơi Cá lớn nuốt cá bé, khi cá lớn nuốt cá bé, cá lớn tăng kích thước. "
            "Dùng khối lệnh nào?"
        ),
        "options": [
            "Đặt kích thước thành 100%",
            "Thay đổi kích thước một lượng",
            "Đổi hiệu ứng màu một lượng",
            "Hiện",
        ],
        "correct": 1,
        "level": "medium",
        "category": "problem_solving",
    },
    {
        "content": "Khi vẽ hình, muốn xóa tất cả nét vẽ trên màn hình, dùng khối lệnh nào?",
        "options": ["Xóa tất cả", "Xóa bản sao", "Xóa nhân vật", "Xóa phông nền"],
        "correct": 0,
        "level": "easy",
        "category": "observation",
    },
    {
        "content": (
            "Trong trò chơi Rắn săn mồi, để rắn dài ra khi chạm mồi, có thể dùng khối lệnh nào?"
        ),
        "options": ["Tạo bản sao của bản thân tôi", "Xóa bản sao này", "Ẩn", "Đổi trang phục"],
        "correct": 0,
        "level": "hard",
        "category": "problem_solving",
    },
    {
        "content": "Muốn cho nhân vật di chuyển lên xuống, cần thay đổi giá trị nào?",
        "options": [
            "Thay đổi x một lượng",
            "Thay đổi y một lượng",
            "Thay đổi kích thước",
            "Thay đổi hiệu ứng màu",
        ],
        "correct": 1,
        "level": "easy",
        "category": "logic",
    },
    {
        "content": "Muốn cho nhân vật di chuyển sang trái phải, cần thay đổi giá trị nào?",
        "options": [
            "Thay đổi x một lượng",
            "Thay đổi y một lượng",
            "Thay đổi kích thước",
            "Thay đổi hướng",
        ],
        "correct": 0,
        "level": "easy",
        "category": "logic",
    },
    {
        "content": "Muốn nhân vật đi lên, ta cần thực hiện lệnh nào?",
        "options": [
            "Thay đổi y một lượng 10",
            "Thay đổi y một lượng -10",
            "Thay đổi x một lượng 10",
            "Thay đổi x một lượng -10",
        ],
        "correct": 0,
        "level": "medium",
        "category": "logic",
    },
    {
        "content": "Muốn nhân vật đi xuống, ta cần thực hiện lệnh nào?",
        "options": [
            "Thay đổi y một lượng 10",
            "Thay đổi y một lượng -10",
            "Thay đổi x một lượng 10",
            "Thay đổi x một lượng -10",
        ],
        "correct": 1,
        "level": "medium",
        "category": "logic",
    },
    {
        "content": "Muốn nhân vật đi sang phải, ta cần thực hiện lệnh nào?",
        "options": [
            "Thay đổi x một lượng 10",
            "Thay đổi x một lượng -10",
            "Thay đổi y một lượng 10",
            "Thay đổi y một lượng -10",
        ],
        "correct": 0,
        "level": "medium",
        "category": "logic",
    },
    {
        "content": "Muốn nhân vật đi sang trái, ta cần thực hiện lệnh nào?",
        "options": [
            "Thay đổi x một lượng 10",
            "Thay đổi x một lượng -10",
            "Thay đổi y một lượng 10",
            "Thay đổi y một lượng -10",
        ],
        "correct": 1,
        "level": "medium",
        "category": "logic",
    },
]

# 2 câu bổ sung chỉ vào bank (không bắt buộc vào quiz)
BANK_EXTRA = [
    {
        "content": (
            "Muốn nhân vật nói «Xin chào» trong 2 giây rồi ẩn đi. Cách nào đúng nhất?"
        ),
        "options": [
            "Nói Xin chào",
            "Nói Xin chào và đợi 2 giây rồi Ẩn",
            "Nghĩ Xin chào",
            "Phát âm thanh Xin chào",
        ],
        "correct": 1,
        "level": "easy",
        "category": "sequencing",
    },
    {
        "content": "Khối «lặp lại mãi» dùng để làm gì?",
        "options": [
            "Chạy đúng 1 lần rồi dừng",
            "Lặp liên tục cho đến khi dừng chương trình",
            "Chỉ lặp khi chạm cạnh sân khấu",
            "Lặp đúng 10 lần rồi dừng",
        ],
        "correct": 1,
        "level": "easy",
        "category": "logic",
    },
]


def _bank_answers(options, correct_idx):
    items = []
    for i, text in enumerate(options):
        items.append({
            "id": str(ObjectId()),
            "answer_text": text,
            "is_correct": i == correct_idx,
        })
    return items


def seed_bank(scratch_course_id):
    """Đảm bảo 14 câu mới (+2 bổ sung) có trong ngân hàng Scratch."""
    col("questions").delete_many({
        "course_id": scratch_course_id,
        "bank_tag": BANK_TAG,
    })
    docs = []
    for i, q in enumerate(NEW_QUESTIONS + BANK_EXTRA):
        docs.append({
            "course_id": scratch_course_id,
            "content": q["content"],
            "image_url": None,
            "level": q["level"],
            "category": q["category"],
            "order_num": 9000 + i,
            "bank_tag": BANK_TAG,
            "answers": _bank_answers(q["options"], q["correct"]),
        })
    col("questions").insert_many(docs)
    print(f"BANK: inserted {len(docs)} questions for Scratch (tag={BANK_TAG})")


def _new_to_quiz_mcq(q):
    opts = [
        {"id": new_id(), "text": t, "is_correct": i == q["correct"]}
        for i, t in enumerate(q["options"])
    ]
    return {
        "id": new_id(),
        "type": "mcq",
        "content": q["content"],
        "image_url": None,
        "points": MCQ_POINTS,
        "order_num": 0,
        "options": opts,
        "explanation": None,
    }


def _bank_doc_to_quiz_mcq(doc):
    options = []
    for a in doc.get("answers") or []:
        text = (a.get("answer_text") or a.get("text") or "").strip()
        if not text:
            continue
        options.append({
            "id": a.get("id") or new_id(),
            "text": text,
            "is_correct": bool(a.get("is_correct")),
        })
    return {
        "id": new_id(),
        "type": "mcq",
        "content": _strip_cau_prefix(doc.get("content") or ""),
        "image_url": doc.get("image_url") or None,
        "points": MCQ_POINTS,
        "order_num": 0,
        "options": options,
        "explanation": None,
    }


def pick_bank_questions(scratch_course_id, exclude_contents, n=BANK_PICK):
    """Lấy n câu từ ngân hàng Scratch có sẵn (không lấy bản tagged scratch_exit trùng 14 câu mới)."""
    exclude_norm = {_strip_cau_prefix(c).lower() for c in exclude_contents}

    candidates = []
    for doc in col("questions").find({"course_id": scratch_course_id}):
        # Bỏ câu vừa seed với tag scratch_exit (trùng nội dung 14 câu mới)
        if doc.get("bank_tag") == BANK_TAG:
            continue
        content = _strip_cau_prefix(doc.get("content") or "")
        if not content:
            continue
        if content.lower() in exclude_norm:
            continue
        answers = doc.get("answers") or []
        if len(answers) < 2:
            continue
        if not any(a.get("is_correct") for a in answers):
            continue
        candidates.append(doc)

    if len(candidates) < n:
        raise RuntimeError(
            f"Ngân hàng Scratch chỉ còn {len(candidates)} câu hợp lệ, cần {n}. "
            "Hãy seed thêm câu hỏi Scratch."
        )

    # Ưu tiên hard rồi medium rồi random
    hard = [c for c in candidates if (c.get("level") or "") == "hard"]
    medium = [c for c in candidates if (c.get("level") or "") == "medium"]
    other = [c for c in candidates if c not in hard and c not in medium]

    picked = []
    random.shuffle(hard)
    random.shuffle(medium)
    random.shuffle(other)
    for pool in (hard, medium, other):
        for doc in pool:
            if len(picked) >= n:
                break
            picked.append(doc)
        if len(picked) >= n:
            break

    return picked[:n]


def build_quiz_questions(scratch_course_id):
    new_mcqs = [_new_to_quiz_mcq(q) for q in NEW_QUESTIONS]
    assert len(new_mcqs) == NEW_COUNT

    bank_docs = pick_bank_questions(
        scratch_course_id,
        exclude_contents=[q["content"] for q in NEW_QUESTIONS],
        n=BANK_PICK,
    )
    bank_mcqs = [_bank_doc_to_quiz_mcq(d) for d in bank_docs]
    assert len(bank_mcqs) == BANK_PICK

    mcqs = new_mcqs + bank_mcqs
    random.shuffle(mcqs)

    # Đánh số lại sau khi xáo
    for i, q in enumerate(mcqs):
        body = _strip_cau_prefix(q["content"])
        q["content"] = f"Câu {i + 1}: {body}"
        q["order_num"] = i
        q["points"] = MCQ_POINTS

    essay = {
        "type": "scratch_file",
        "content": (
            "BẰNG KIẾN THỨC ĐÃ HỌC, HÃY XÂY DỰNG 1 BÀI LÀM TÂM ĐẮC NHẤT TRÊN SCRATCH.\n\n"
            "VÍ DỤ: cá lớn nuốt cá bé, rắn săn mồi, vẽ hoa...\n\n"
            "Nộp file Scratch (.sb3) ở đây."
        ),
        "points": ESSAY_POINTS,
        "order_num": len(mcqs),
        "hint": (
            "30 câu trắc nghiệm chiếm 60% điểm (tự chấm, đã xáo thứ tự). "
            "Phần tự luận chiếm 40% — thầy xem chạy file .sb3 trên web rồi chấm."
        ),
        "accept_extensions": [".sb3", ".sb2"],
    }

    raw = mcqs + [essay]
    print(f"QUIZ MCQ: {NEW_COUNT} new + {BANK_PICK} from bank = {len(mcqs)} (shuffled)")
    return sanitize_questions(raw)


def main():
    app = create_app()
    with app.app_context():
        course = col("courses").find_one({"slug": "scratch"})
        if not course:
            raise RuntimeError("Chưa có khóa Scratch — chạy seed.py trước")
        scratch_id = oid_str(course["_id"])
        seed_bank(scratch_id)

        questions = build_quiz_questions(scratch_id)
        description = (
            "Kiểm tra đầu ra Scratch: 30 câu trắc nghiệm xáo trộn "
            "(14 câu mới + 16 câu ngân hàng, 60% tự chấm) "
            "+ 1 câu tự luận nộp file .sb3 (40%, giáo viên chấm)."
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
                        "duration_minutes": 75,
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
                "duration_minutes": 75,
            })
            data = quiz_to_dict(existing, include_answers=True)
            print("UPDATED")
        else:
            if col("quizzes").find_one({"slug": FIXED_SLUG}):
                slug = None
                for _ in range(20):
                    candidate = generate_quiz_slug()
                    if not col("quizzes").find_one({"slug": candidate}):
                        slug = candidate
                        break
                if not slug:
                    raise RuntimeError("Không tạo được slug")
            else:
                slug = FIXED_SLUG

            doc = {
                "title": QUIZ_TITLE,
                "description": description,
                "slug": slug,
                "duration_minutes": 75,
                "is_active": True,
                "questions": questions,
                "created_at": now,
                "updated_at": now,
            }
            result = col("quizzes").insert_one(doc)
            doc["_id"] = result.inserted_id
            data = quiz_to_dict(doc, include_answers=True)
            print("CREATED")

        mcq_n = sum(1 for q in data["questions"] if q.get("type") == "mcq")
        print(f"id={data['id']}")
        print(f"slug={data['slug']}")
        print(f"questions={len(data['questions'])} (mcq={mcq_n})")
        print(f"max_score={data['max_score']}")
        print(f"public=/quiz/{data['slug']}")


if __name__ == "__main__":
    main()
