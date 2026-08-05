"""Tạo quiz Scratch kiểm tra tháng 1: 15 câu khó từ bank + 5 câu mới."""

from datetime import datetime
from bson import ObjectId

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col
from services.quiz_service import generate_quiz_slug, quiz_to_dict, sanitize_questions, new_id


def oid():
    return str(ObjectId())


NEW_HARD_QUESTIONS = [
    {
        "content": "Chức năng nào sau đây KHÔNG phải là chức năng của biến trong Scratch?",
        "level": "hard",
        "category": "logic",
        "answers": [
            {"text": "Lưu trữ một giá trị (số, chữ) để dùng lại", "is_correct": False},
            {"text": "Đếm điểm số trong trò chơi", "is_correct": False},
            {"text": "Tự động vẽ hình và đổi trang phục nhân vật", "is_correct": True},
            {"text": "Thay đổi giá trị khi nhân vật chạm vật thể", "is_correct": False},
        ],
    },
    {
        "content": "Muốn vẽ hình tròn có bán kính R thì khối lệnh nào sau đây là đúng?",
        "level": "hard",
        "category": "algorithm",
        "answers": [
            {
                "text": "Lặp 360 lần: di chuyển (2 × π × R / 360) bước, xoay phải 1 độ",
                "is_correct": True,
            },
            {
                "text": "Lặp 4 lần: di chuyển R bước, xoay phải 90 độ",
                "is_correct": False,
            },
            {
                "text": "Di chuyển R bước rồi xoay phải 360 độ một lần",
                "is_correct": False,
            },
            {
                "text": "Lặp R lần: di chuyển 360 bước, xoay phải 2 độ",
                "is_correct": False,
            },
        ],
    },
    {
        "content": (
            "Trong trò chơi kiểu Flappy Bird, khi con vịt đang rơi xuống "
            "(không nhảy), khối lệnh nào thường được dùng?"
        ),
        "level": "hard",
        "category": "problem_solving",
        "answers": [
            {"text": "Thay đổi y đi một số âm (ví dụ thay đổi y đi -3)", "is_correct": True},
            {"text": "Thay đổi x đi 10", "is_correct": False},
            {"text": "Đặt hướng 90 độ", "is_correct": False},
            {"text": "Đổi trang phục sang trang phục tiếp theo", "is_correct": False},
        ],
    },
    {
        "content": (
            "Em có biến «điểm». Khi nhân vật chạm vào sao, muốn cộng thêm 1 điểm. "
            "Khối lệnh nào đúng?"
        ),
        "level": "hard",
        "category": "logic",
        "answers": [
            {"text": "Đặt «điểm» thành 1", "is_correct": False},
            {"text": "Thay đổi «điểm» đi 1", "is_correct": True},
            {"text": "Đặt «điểm» thành 0", "is_correct": False},
            {"text": "Ẩn biến «điểm»", "is_correct": False},
        ],
    },
    {
        "content": (
            "Muốn nhân vật liên tục rơi xuống cho đến khi chạm mặt đất, "
            "cách làm nào đúng nhất?"
        ),
        "level": "hard",
        "category": "algorithm",
        "answers": [
            {
                "text": "Lặp lại mãi: nếu không chạm màu đất thì thay đổi y đi số âm",
                "is_correct": True,
            },
            {
                "text": "Chỉ dùng «đi đến x:0 y:0» một lần",
                "is_correct": False,
            },
            {
                "text": "Xoay phải 15 độ trong khối «khi nhấn phím mũi tên»",
                "is_correct": False,
            },
            {
                "text": "Đặt kích thước thành 100%",
                "is_correct": False,
            },
        ],
    },
]


def bank_to_quiz_mcq(q, points=1, order=0):
    options = []
    for a in q.get("answers") or []:
        options.append({
            "id": a.get("id") or new_id(),
            "text": a.get("answer_text") or a.get("text") or "",
            "is_correct": bool(a.get("is_correct")),
        })
    return {
        "id": new_id(),
        "type": "mcq",
        "content": q.get("content") or "",
        "image_url": q.get("image_url") or None,
        "points": points,
        "order_num": order,
        "options": options,
    }


def main():
    app = create_app()
    with app.app_context():
        course = col("courses").find_one({"slug": "scratch"})
        if not course:
            raise SystemExit("No Scratch course")
        course_id = str(course["_id"])

        # Ensure 5 new bank questions exist (by content match)
        max_order = 0
        for q in col("questions").find({"course_id": course_id}):
            max_order = max(max_order, int(q.get("order_num") or 0))

        inserted_bank = []
        for raw in NEW_HARD_QUESTIONS:
            existing = col("questions").find_one({
                "course_id": course_id,
                "content": raw["content"],
            })
            if existing:
                inserted_bank.append(existing)
                print("bank exists order", existing.get("order_num"))
                continue
            max_order += 1
            answers = []
            for a in raw["answers"]:
                answers.append({
                    "id": oid(),
                    "answer_text": a["text"],
                    "is_correct": a["is_correct"],
                })
            doc = {
                "course_id": course_id,
                "content": raw["content"],
                "image_url": None,
                "level": "hard",
                "category": raw["category"],
                "order_num": max_order,
                "answers": answers,
            }
            res = col("questions").insert_one(doc)
            doc["_id"] = res.inserted_id
            inserted_bank.append(doc)
            print("bank inserted order", max_order)

        # 15 hardest from bank: all hard first, then medium fill — exclude the 5 new ones for variety in the 15
        new_ids = {str(q["_id"]) for q in inserted_bank}
        hard = list(
            col("questions")
            .find({"course_id": course_id, "level": "hard", "_id": {"$nin": [q["_id"] for q in inserted_bank]}})
            .sort("order_num", 1)
        )
        medium = list(
            col("questions")
            .find({"course_id": course_id, "level": "medium"})
            .sort([("order_num", -1)])
        )
        picked = list(hard)
        if len(picked) < 15:
            picked.extend(medium[: 15 - len(picked)])
        picked = picked[:15]
        print("picked", len(picked), "hard_old", len(hard))

        # Avoid duplicate quiz
        existing_quiz = col("quizzes").find_one({
            "title": "Bài tập Scratch — Kiểm tra tháng 1",
        })
        if existing_quiz:
            print("QUIZ_EXISTS", existing_quiz.get("slug"), str(existing_quiz["_id"]))
            return

        quiz_questions_raw = []
        for i, q in enumerate(picked):
            quiz_questions_raw.append(bank_to_quiz_mcq(q, points=1, order=i))
        for i, q in enumerate(inserted_bank):
            mapped = {
                "content": q["content"],
                "image_url": q.get("image_url"),
                "answers": q.get("answers") or [],
            }
            quiz_questions_raw.append(bank_to_quiz_mcq(mapped, points=1, order=15 + i))

        questions = sanitize_questions(quiz_questions_raw)
        slug = None
        for _ in range(20):
            candidate = generate_quiz_slug()
            if not col("quizzes").find_one({"slug": candidate}):
                slug = candidate
                break

        now = datetime.utcnow()
        quiz_doc = {
            "title": "Bài tập Scratch — Kiểm tra tháng 1",
            "description": (
                "20 cau trac nghiem Scratch: 15 cau kho tu ngan hang + 5 cau nang cao "
                "ve bien va khoi lenh. Thoi gian 30 phut."
            ),
            "slug": slug,
            "duration_minutes": 30,
            "is_active": True,
            "questions": questions,
            "created_at": now,
            "updated_at": now,
        }
        # Fix description to proper Vietnamese
        quiz_doc["description"] = (
            "20 câu trắc nghiệm Scratch: 15 câu khó từ ngân hàng + 5 câu nâng cao "
            "về biến và khối lệnh. Thời gian 30 phút."
        )
        result = col("quizzes").insert_one(quiz_doc)
        quiz_doc["_id"] = result.inserted_id
        data = quiz_to_dict(quiz_doc, include_answers=True)
        print("CREATED_QUIZ")
        print("id=" + data["id"])
        print("slug=" + data["slug"])
        print("questions=" + str(data["question_count"]))
        print("public=/quiz/" + data["slug"])
        print("edit=/admin/quizzes/" + data["id"] + "/edit")
        print("bank_new=" + str(len(inserted_bank)))


if __name__ == "__main__":
    main()
