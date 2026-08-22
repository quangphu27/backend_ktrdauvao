"""Xuất câu hỏi Scratch mức trung bình + khó ra JSON."""

import json
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from database import col


def main():
    app = create_app()
    with app.app_context():
        course = col("courses").find_one({"slug": "scratch"})
        if not course:
            raise SystemExit("Không tìm thấy khóa Scratch")

        cid = str(course["_id"])
        docs = list(
            col("questions")
            .find({"course_id": cid, "level": {"$in": ["medium", "hard"]}})
            .sort([("level", 1), ("order_num", 1)])
        )

        medium = sum(1 for d in docs if d.get("level") == "medium")
        hard = sum(1 for d in docs if d.get("level") == "hard")

        questions = []
        for i, d in enumerate(docs, 1):
            answers = []
            correct = []
            for a in d.get("answers") or []:
                text = a.get("answer_text") or a.get("text") or ""
                answers.append(text)
                if a.get("is_correct"):
                    correct.append(text)

            item = {
                "stt": i,
                "level": d.get("level"),
                "category": d.get("category"),
                "cau_hoi": d.get("content"),
                "dap_an": answers,
                "dap_an_dung": correct[0] if len(correct) == 1 else correct,
            }
            if d.get("image_url"):
                item["image_url"] = d["image_url"]
            questions.append(item)

        path = "scratch_questions_medium_hard.json"
        payload = {
            "course": "Scratch",
            "levels": ["medium", "hard"],
            "total": len(questions),
            "medium_count": medium,
            "hard_count": hard,
            "questions": questions,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        print(f"OK total={len(questions)} medium={medium} hard={hard}")
        print(f"file={path}")


if __name__ == "__main__":
    main()
