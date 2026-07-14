"""Cập nhật cột Nhận xét trong file ket_qua_kiem_tra từ DB."""
import os
import sys

import xlrd
from openpyxl import Workbook

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import col
from export_student_reports import _load_tests
from services.scoring import get_recommendation

XLS_IN = os.path.join(os.path.dirname(__file__), "uploads", "ket_qua_kiem_tra.xls")
XLS_OUT = os.path.join(os.path.dirname(__file__), "uploads", "ket_qua_kiem_tra.xlsx")


def _norm(s):
    return " ".join((s or "").strip().lower().split())


def _build_comment_map():
    items = _load_tests(all_db=True)
    mapping = {}
    for item in items:
        t = item["test"]
        key = (_norm(t.get("student_name")), _norm(t.get("course_name")))
        mapping[key] = item["comment"]
    return mapping


def refresh():
    if not os.path.exists(XLS_IN):
        print(f"Khong tim thay: {XLS_IN}")
        return None

    comment_map = _build_comment_map()
    wb_in = xlrd.open_workbook(XLS_IN)
    sh = wb_in.sheet_by_index(0)
    headers = [str(sh.cell_value(0, c)) for c in range(sh.ncols)]

    comment_col = next(
        (i for i, h in enumerate(headers) if "nhận xét" in h.lower() or "nhan xet" in h.lower()),
        sh.ncols - 1,
    )
    name_col = next((i for i, h in enumerate(headers) if "học sinh" in h.lower()), 0)
    course_col = next((i for i, h in enumerate(headers) if "khóa" in h.lower()), None)

    wb_out = Workbook()
    ws = wb_out.active
    ws.append(headers)

    updated = 0
    for r in range(1, sh.nrows):
        row = [sh.cell_value(r, c) for c in range(sh.ncols)]
        name = str(row[name_col]) if name_col is not None else ""
        course = str(row[course_col]) if course_col is not None else ""
        key = (_norm(name), _norm(course))
        if key in comment_map:
            row[comment_col] = comment_map[key]
            updated += 1
        ws.append(row)

    wb_out.save(XLS_OUT)
    print(f"Da cap nhat {updated}/{sh.nrows - 1} dong -> {XLS_OUT}")
    return XLS_OUT


if __name__ == "__main__":
    refresh()
