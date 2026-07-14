"""Xuất ảnh phản hồi kiểm tra — mỗi học sinh 1 file PNG.

Cách dùng:
  python export_feedback_images.py
  python export_feedback_images.py --all-db
"""
import os
import sys

from export_student_reports import DEFAULT_IDS, _load_tests
from services.export import feedback_image_filename
from services.feedback_card import build_feedback_data, render_feedback_card


def export_images(test_ids=None, all_db=False, out_dir=None):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = out_dir or os.path.join(base, "exports", "nhan-xet-hoc-sinh", "Nhan_xet")
    os.makedirs(out_dir, exist_ok=True)

    items = _load_tests(test_ids, all_db=all_db)
    if not items:
        print("Khong co bai lam nao de xuat.")
        return []

    paths = []
    for item in items:
        test = item["test"]
        data = build_feedback_data(test, item["comment"])
        filename = feedback_image_filename(test)
        path = os.path.join(out_dir, filename)
        render_feedback_card(data, path)
        paths.append(path)
        print("  saved:", len(paths))

    print(f"\nDa xuat {len(paths)} anh -> {out_dir}")
    return paths


if __name__ == "__main__":
    args = sys.argv[1:]
    all_db = "--all-db" in args
    if all_db:
        args = [a for a in args if a != "--all-db"]
    export_images(args if args else None, all_db=all_db)
