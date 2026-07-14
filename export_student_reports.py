"""Xuất 1 file Excel tổng hợp nhận xét chi tiết tất cả học sinh.

Cách dùng:
  python export_student_reports.py
  python export_student_reports.py --all-db          # mọi bài trong DB
  python export_student_reports.py <test_id> ...
"""
import os
import sys

from app import create_app
from config import Config
from database import col, parse_oid
from models import test_to_dict
from services.export import export_all_students_to_path
from services.scoring import get_recommendation
from services.student_comment import generate_student_comment

DEFAULT_IDS = """
6a3a6a64cb6b65ed23f76f91 6a3a69e9cb6b65ed23f76f90 6a3a69e1cb6b65ed23f76f8f
6a3a69d2cb6b65ed23f76f8e 6a3a689ccb6b65ed23f76f8d 6a3a684bcb6b65ed23f76f8c
6a3a66a5cb6b65ed23f76f8b 6a39252b4a03bd22259849bf 6a3920cb8f3f013a56ad8569
6a391d4b1459ec656db65554 6a391d261459ec656db65553 6a391c871459ec656db65552
6a391c6c1459ec656db65551 6a391c2b1459ec656db65550 6a391c0c1459ec656db6554f
6a391bb81459ec656db6554e 6a391b821459ec656db6554d 6a391a761459ec656db6554c
6a3919cb1459ec656db6554b 6a3919151459ec656db6554a 6a3918581459ec656db65549
6a3918531459ec656db65548 6a3918421459ec656db65547 6a3917a11459ec656db65546
6a39170b1459ec656db65545 6a3916bc1459ec656db65544 6a39169f1459ec656db65543
6a3916261459ec656db65542 6a3916011459ec656db65541 6a3915f41459ec656db65540
6a3915401459ec656db6553f
""".split()


def _load_tests(test_ids=None, all_db=False):
    app = create_app()
    items = []
    with app.app_context():
        if all_db:
            docs = col("tests").find().sort("submitted_at", -1)
        else:
            ids = test_ids or DEFAULT_IDS
            docs = []
            for tid in ids:
                tid = tid.strip()
                if not tid:
                    continue
                doc = col("tests").find_one({"_id": parse_oid(tid)})
                if doc:
                    docs.append(doc)

        for doc in docs:
            test = test_to_dict(doc, include_details=True)
            slug = (test.get("course_name") or "").lower()
            test["recommendation"] = get_recommendation(
                slug,
                float(test.get("score") or 0),
                test.get("student_phone"),
                test.get("student_name"),
            )
            comment = generate_student_comment(test)
            items.append({"test": test, "comment": comment})
    return items


def export_reports(test_ids=None, all_db=False, out_path=None):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base, "exports", "nhan-xet-hoc-sinh")
    out_path = out_path or os.path.join(out_dir, "TAT_CA_HOC_SINH_NHAN_XET.xlsx")

    frontend_url = os.getenv("FRONTEND_URL", getattr(Config, "FRONTEND_URL", None))
    items = _load_tests(test_ids, all_db=all_db)

    if not items:
        print("Khong co bai lam nao de xuat.")
        return None

    path = export_all_students_to_path(items, out_path, frontend_url)
    print(f"Da xuat {len(items)} hoc sinh -> {path}")
    return path


if __name__ == "__main__":
    args = sys.argv[1:]
    all_db = "--all-db" in args
    if all_db:
        args = [a for a in args if a != "--all-db"]
    export_reports(args if args else None, all_db=all_db)
