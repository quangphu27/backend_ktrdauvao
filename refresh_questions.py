"""Cập nhật lại ngân hàng câu hỏi từ seed (xóa cũ + thêm mới theo từng khóa học)."""
from seed import SCRATCH_QUESTIONS, PYTHON_QUESTIONS, _add_questions
from database import col, oid_str
from validate_questions import validate_all


def refresh_course(slug, questions_data):
    course = col("courses").find_one({"slug": slug})
    if not course:
        print(f"Khong tim thay khoa hoc: {slug}")
        return 0
    course_id = oid_str(course["_id"])
    deleted = col("questions").delete_many({"course_id": course_id}).deleted_count
    _add_questions(course_id, questions_data)
    added = len(questions_data)
    print(f"  {slug}: xoa {deleted} cau, them {added} cau moi")
    return added


def refresh_all():
    total = 0
    total += refresh_course("scratch", SCRATCH_QUESTIONS)
    total += refresh_course("python", PYTHON_QUESTIONS)
    errors = validate_all()
    if errors:
        for e in errors:
            print(f"  LOI: {e}")
        raise RuntimeError(f"Cap nhat xong nhung validation that bai ({len(errors)} loi)")
    print(f"Tong: {total} cau hoi da cap nhat. Validation: OK.")
    return total


if __name__ == "__main__":
    from app import create_app

    app = create_app()
    with app.app_context():
        refresh_all()
