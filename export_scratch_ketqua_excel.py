"""Cập nhật 4 file phiếu nhận xét Scratch:
- Cột Điểm = chỉ điểm trắc nghiệm (/100)
- Cột «Xem bài làm» (bên phải Nhận xét) → hyperlink sang sheet chi tiết HS
- Mỗi học sinh 1 sheet: câu hỏi, đủ đáp án, đáp án đúng, HS chọn
"""
from __future__ import annotations

import os
import re
import sys

from bson import ObjectId
from dotenv import load_dotenv
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from pymongo import MongoClient

load_dotenv()

QUIZ_ID = "6ab7e539c4110429822a0cb0"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KETQUA_DIR = os.path.join(ROOT, "frontend", "public", "ketqua")

CLASSES = [
    {"file": "Scratch 1.xlsx", "grade_keys": {"Scratch1", "Scratch 1"}, "label": "Scratch1"},
    {"file": "Scratch 2.xlsx", "grade_keys": {"Scratch2", "Scratch 2"}, "label": "Scratch2"},
    {"file": "Scratch 3.xlsx", "grade_keys": {"Scratch3", "Scratch 3"}, "label": "Scratch3"},
    {"file": "Scratch 4.xlsx", "grade_keys": {"Scratch4", "Scratch 4"}, "label": "Scratch4"},
]

HEADER_FILL = PatternFill("solid", fgColor="1E78C8")
HEADER_FONT = Font(bold=True, color="FFFFFF")
OK_FILL = PatternFill("solid", fgColor="C6EFCE")
BAD_FILL = PatternFill("solid", fgColor="FFC7CE")
LINK_FONT = Font(color="0563C1", underline="single", bold=True)
THIN = Border(
    left=Side(style="thin", color="B0C4DE"),
    right=Side(style="thin", color="B0C4DE"),
    top=Side(style="thin", color="B0C4DE"),
    bottom=Side(style="thin", color="B0C4DE"),
)

# Theme trang trí sheet chi tiết
FILL_BANNER = PatternFill("solid", fgColor="0F4C81")
FILL_BANNER2 = PatternFill("solid", fgColor="1E78C8")
FILL_TOC = PatternFill("solid", fgColor="E8F2FC")
FILL_CARD_OK = PatternFill("solid", fgColor="EAF7EF")
FILL_CARD_BAD = PatternFill("solid", fgColor="FDECEC")
FILL_OPT_CORRECT = PatternFill("solid", fgColor="B7E4C7")
FILL_OPT_WRONG_PICK = PatternFill("solid", fgColor="F8B4B4")
FILL_OPT_NORMAL = PatternFill("solid", fgColor="FFFFFF")
FILL_BTN_OK = PatternFill("solid", fgColor="2D9F5B")
FILL_BTN_BAD = PatternFill("solid", fgColor="D64545")
FILL_WHITE = PatternFill("solid", fgColor="FFFFFF")
FILL_SOFT = PatternFill("solid", fgColor="F7FAFD")
FONT_WHITE_BOLD = Font(bold=True, color="FFFFFF", size=12)
FONT_TITLE = Font(bold=True, color="FFFFFF", size=18)
FONT_SUB = Font(bold=True, color="E8F2FC", size=12)
FONT_Q = Font(bold=True, color="0F4C81", size=12)
FONT_BODY = Font(color="1F2A37", size=11)
FONT_MUTED = Font(color="5B6B7C", size=10)
FONT_OK = Font(bold=True, color="1B7A3D", size=11)
FONT_BAD = Font(bold=True, color="A61B1B", size=11)
FONT_BTN = Font(bold=True, color="FFFFFF", size=10)
MED = Border(
    left=Side(style="medium", color="9DB7D4"),
    right=Side(style="medium", color="9DB7D4"),
    top=Side(style="medium", color="9DB7D4"),
    bottom=Side(style="medium", color="9DB7D4"),
)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
LETTERS = "ABCDEFGH"


def normalize_name(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def set_internal_sheet_link(cell, sheet_name: str, display: str = "Xem bài làm", cell_ref: str = "A1"):
    """Link nội bộ sheet — tương thích Excel + WPS.

    Dùng công thức HYPERLINK(#...'!A1) thay vì hyperlink file ngoài
    (openpyxl string target khiến WPS báo «Không thể mở tệp»).
    """
    escaped = (sheet_name or "").replace("'", "''")
    # Xóa relationship/target cũ nếu có
    try:
        cell.hyperlink = None
    except Exception:
        pass
    cell.value = f'=HYPERLINK("#\'{escaped}\'!{cell_ref}","{display}")'
    cell.font = LINK_FONT
    cell.alignment = Alignment(horizontal="center", vertical="center")


def _paint(ws, row, col1, col2, fill=None, border=None):
    for c in range(col1, col2 + 1):
        cell = ws.cell(row, c)
        if fill is not None:
            cell.fill = fill
        if border is not None:
            cell.border = border


def _merge_set(ws, r1, c1, r2, c2, value, font=None, fill=None, align=None, border=None):
    if r1 != r2 or c1 != c2:
        ws.merge_cells(start_row=r1, start_column=c1, end_row=r2, end_column=c2)
    cell = ws.cell(r1, c1, value)
    if font:
        cell.font = font
    if fill:
        cell.fill = fill
    if align:
        cell.alignment = align
    if border:
        for rr in range(r1, r2 + 1):
            for cc in range(c1, c2 + 1):
                ws.cell(rr, cc).border = border
                if fill:
                    ws.cell(rr, cc).fill = fill
    return cell


def sheet_title_for(name: str, used: set) -> str:
    """Tên sheet Excel ≤31 ký tự, không ký tự cấm."""
    base = re.sub(r'[\\/*?:\[\]]', "", (name or "HS").strip()) or "HS"
    base = base[:31]
    title = base
    n = 2
    while title in used:
        suffix = f"_{n}"
        title = base[: 31 - len(suffix)] + suffix
        n += 1
    used.add(title)
    return title


def mc_score_100(details):
    mc = [d for d in details if d.get("type") == "mcq"]
    earned = sum(int(d.get("points_awarded") or 0) for d in mc)
    max_pts = sum(int(d.get("points") or 0) for d in mc)
    if max_pts <= 0:
        return None, earned, max_pts, mc
    return round(earned / max_pts * 100, 1), earned, max_pts, mc


def format_score(mc100):
    if mc100 is None:
        return "—"
    if float(mc100) == int(mc100):
        return f"{int(mc100)}/100"
    return f"{mc100}/100"


def find_attempt(attempts, name, grade_keys):
    key = normalize_name(name)
    same_grade = []
    any_match = []
    for a in attempts:
        if normalize_name(a.get("student_name") or "") != key:
            continue
        any_match.append(a)
        if (a.get("student_grade") or "").strip() in grade_keys:
            same_grade.append(a)
    pool = same_grade or any_match
    if not pool:
        return None
    # bài nộp mới nhất
    return sorted(
        pool,
        key=lambda x: x.get("submitted_at") or "",
        reverse=True,
    )[0]


def quiz_mc_by_id(quiz):
    out = {}
    for q in quiz.get("questions") or []:
        if q.get("type") != "mcq":
            continue
        out[str(q.get("id"))] = q
    return out


def option_texts(qdoc):
    opts = (qdoc or {}).get("options") or []
    texts = []
    for o in opts:
        if isinstance(o, dict):
            texts.append((o.get("text") or "").strip())
        else:
            texts.append(str(o))
    # pad to 4
    while len(texts) < 4:
        texts.append("")
    return texts[:8]  # allow up to 8


def correct_from_question(qdoc, detail_correct):
    if detail_correct:
        return detail_correct
    for o in (qdoc or {}).get("options") or []:
        if isinstance(o, dict) and o.get("is_correct"):
            return (o.get("text") or "").strip()
    return ""


def read_roster(ws):
    """Đọc danh sách HS từ sheet phiếu (dòng header có 'Họ và tên')."""
    header_row = None
    col_name = col_score = col_comment = None
    for r in range(1, min(ws.max_row or 1, 30) + 1):
        vals = [ws.cell(r, c).value for c in range(1, 8)]
        joined = " ".join(str(v) for v in vals if v)
        if "Họ và tên" in joined or "Ho va ten" in joined:
            header_row = r
            for c in range(1, 10):
                v = str(ws.cell(r, c).value or "")
                if "Họ và tên" in v or "tên học sinh" in v.lower():
                    col_name = c
                elif v.strip() in ("Điểm", "Diem"):
                    col_score = c
                elif "Nhận xét" in v or "Nhan xet" in v:
                    col_comment = c
            break
    if not header_row or not col_name:
        raise RuntimeError("Không tìm thấy header danh sách học sinh")

    students = []
    for r in range(header_row + 1, (ws.max_row or header_row) + 1):
        name = ws.cell(r, col_name).value
        if not name or not str(name).strip():
            # dừng khi gặp ghi chú / footer
            stt = ws.cell(r, 1).value
            if stt is None and not ws.cell(r, col_comment).value:
                continue
            if isinstance(name, str) and name.startswith("Ghi chú"):
                break
            if stt is None:
                break
            continue
        name = str(name).strip()
        if name.startswith("Ghi chú") or name.startswith("©"):
            break
        students.append(
            {
                "row": r,
                "name": name,
                "comment": ws.cell(r, col_comment).value if col_comment else None,
            }
        )
    return {
        "header_row": header_row,
        "col_name": col_name,
        "col_score": col_score or 3,
        "col_comment": col_comment or 4,
        "students": students,
    }


def clear_extra_sheets(wb, keep_title):
    for title in list(wb.sheetnames):
        if title == keep_title:
            continue
        del wb[title]


def write_student_sheet(wb, title, student_name, grade, mc100, earned, max_pts, mc_details, qmap):
    """Sheet đẹp: mục lục Câu 1..N (bấm để nhảy) + thẻ chi tiết từng câu."""
    ws = wb.create_sheet(title)
    n = len(mc_details)
    correct_n = sum(1 for d in mc_details if d.get("is_correct"))
    wrong_n = n - correct_n
    cols = 10  # A–J

    for c, w in enumerate([14, 14, 14, 14, 14, 14, 14, 14, 14, 14], 1):
        ws.column_dimensions[get_column_letter(c)].width = w
    ws.sheet_view.showGridLines = False

    # ---- Banner ----
    _merge_set(ws, 1, 1, 1, cols, f"CHI TIẾT BÀI LÀM — {student_name}", FONT_TITLE, FILL_BANNER, CENTER)
    ws.row_dimensions[1].height = 32
    _merge_set(
        ws, 2, 1, 2, cols,
        f"Lớp {grade}   ·   Điểm trắc nghiệm: {format_score(mc100)}   ·   Raw {earned}/{max_pts}   ·   Đúng {correct_n}/{n}   ·   Sai {wrong_n}",
        FONT_SUB, FILL_BANNER2, CENTER,
    )
    ws.row_dimensions[2].height = 22

    # ---- Mục lục ----
    _merge_set(
        ws, 4, 1, 4, cols,
        "MỤC LỤC CÂU HỎI  ·  Bấm vào «Câu …» để xem chi tiết bên dưới",
        Font(bold=True, color="0F4C81", size=12), FILL_TOC, CENTER, THIN,
    )
    ws.row_dimensions[4].height = 22

    # Tính trước vị trí bắt đầu mỗi thẻ câu (sau mục lục)
    per_row = 10
    toc_rows = max(1, (n + per_row - 1) // per_row)
    toc_start = 5
    detail_start = toc_start + toc_rows + 2  # 1 dòng chú thích màu + 1 trống

    # Mỗi câu: 9 dòng (tiêu đề, đề, 4 đáp án, tóm tắt, spacer, back)
    ROWS_PER_Q = 9
    q_anchors = {}
    for i in range(n):
        q_anchors[i + 1] = detail_start + i * ROWS_PER_Q

    # Nút mục lục Câu 1..N
    for i in range(n):
        qnum = i + 1
        ok = bool(mc_details[i].get("is_correct"))
        r = toc_start + (i // per_row)
        c = (i % per_row) + 1
        cell = ws.cell(r, c)
        set_internal_sheet_link(cell, title, f"Câu {qnum}", f"A{q_anchors[qnum]}")
        cell.fill = FILL_BTN_OK if ok else FILL_BTN_BAD
        cell.font = FONT_BTN
        cell.border = THIN
        cell.alignment = CENTER
        ws.row_dimensions[r].height = 22

    legend_row = toc_start + toc_rows
    _merge_set(
        ws, legend_row, 1, legend_row, cols,
        "Chú thích mục lục:  xanh = đúng   ·   đỏ = sai   ·   Bên dưới mỗi câu có đủ đáp án A–D, đáp án đúng và đáp án học sinh chọn",
        FONT_MUTED, FILL_SOFT, LEFT,
    )

    # ---- Thẻ chi tiết từng câu ----
    for i, d in enumerate(mc_details):
        qnum = i + 1
        r0 = q_anchors[qnum]
        qid = str(d.get("question_id") or "")
        qdoc = qmap.get(qid) or {}
        opts = [t for t in option_texts(qdoc) if t] or []
        # đảm bảo có đủ options nếu detail có đáp án không nằm trong list
        correct = correct_from_question(qdoc, d.get("correct_answer"))
        student = (d.get("student_answer") or "").strip() or "(trống)"
        ok = bool(d.get("is_correct"))
        content = (d.get("content") or qdoc.get("content") or "").strip()
        card_fill = FILL_CARD_OK if ok else FILL_CARD_BAD
        result_txt = "✓ ĐÚNG" if ok else "✗ SAI"

        # Hàng tiêu đề câu
        _merge_set(
            ws, r0, 1, r0, 7,
            f"Câu {qnum}",
            Font(bold=True, color="FFFFFF", size=14),
            FILL_BANNER if ok else PatternFill("solid", fgColor="A61B1B"),
            LEFT,
            MED,
        )
        badge = ws.cell(r0, 8, result_txt)
        badge.fill = FILL_BTN_OK if ok else FILL_BTN_BAD
        badge.font = FONT_BTN
        badge.alignment = CENTER
        badge.border = MED
        ws.merge_cells(start_row=r0, start_column=8, end_row=r0, end_column=9)
        back = ws.cell(r0, 10)
        set_internal_sheet_link(back, title, "↑ Mục lục", "A4")
        back.fill = FILL_BANNER2
        back.font = FONT_BTN
        back.border = MED
        ws.row_dimensions[r0].height = 26

        # Đề bài
        _merge_set(ws, r0 + 1, 1, r0 + 1, cols, content, FONT_Q, card_fill, LEFT, THIN)
        ws.row_dimensions[r0 + 1].height = max(36, 18 * (1 + content.count("\n")))

        # 4 đáp án A–D (hoặc nhiều hơn tối đa 4 dòng cố định trong card)
        # Nếu thiếu option, vẫn hiện 4 dòng
        display_opts = (opts + ["", "", "", ""])[:4]
        for oi, opt in enumerate(display_opts):
            rr = r0 + 2 + oi
            letter = LETTERS[oi]
            label = f"{letter}. {opt}" if opt else f"{letter}."
            is_correct_opt = bool(opt) and opt == correct
            is_student_opt = bool(opt) and opt == student
            if is_correct_opt:
                fill = FILL_OPT_CORRECT
                suffix = "   ← Đáp án đúng"
                font = FONT_OK
            elif is_student_opt and not ok:
                fill = FILL_OPT_WRONG_PICK
                suffix = "   ← Học sinh chọn (sai)"
                font = FONT_BAD
            else:
                fill = FILL_OPT_NORMAL if oi % 2 == 0 else FILL_SOFT
                suffix = ""
                font = FONT_BODY
            if is_student_opt and is_correct_opt:
                suffix = "   ← Học sinh chọn (đúng)"
            _merge_set(ws, rr, 1, rr, cols, label + suffix, font, fill, LEFT, THIN)
            ws.row_dimensions[rr].height = 20

        # Tóm tắt
        summary = f"Đáp án đúng: {correct or '—'}     |     Học sinh chọn: {student}"
        _merge_set(
            ws, r0 + 6, 1, r0 + 6, cols,
            summary,
            FONT_OK if ok else FONT_BAD,
            OK_FILL if ok else BAD_FILL,
            LEFT,
            THIN,
        )
        ws.row_dimensions[r0 + 6].height = 22

        # Spacer
        _paint(ws, r0 + 7, 1, cols, FILL_WHITE)
        ws.row_dimensions[r0 + 7].height = 10
        # hàng dự phòng trong ROWS_PER_Q
        _paint(ws, r0 + 8, 1, cols, FILL_WHITE)
        ws.row_dimensions[r0 + 8].height = 6

    # Nút về phiếu (góc trên không — thêm dòng cuối)
    end_row = detail_start + n * ROWS_PER_Q + 1
    _merge_set(
        ws, end_row, 1, end_row, cols,
        "Hết danh sách câu hỏi  ·  Bấm «↑ Mục lục» trên mỗi câu để quay lại chọn câu khác",
        FONT_MUTED, FILL_TOC, CENTER,
    )

    ws.freeze_panes = "A5"
    ws.print_title_rows = "1:4"
    return ws


def process_class(wb_path, grade_keys, label, attempts, qmap):
    wb = load_workbook(wb_path)
    main = wb.active
    main_title = main.title
    roster = read_roster(main)
    header_row = roster["header_row"]
    col_score = roster["col_score"]
    col_comment = roster["col_comment"]
    col_link = col_comment + 1

    # Xóa sheet phụ cũ (Chi_tiet_TN, Anh_TN, sheet HS cũ…)
    clear_extra_sheets(wb, main_title)
    main = wb[main_title]

    # Header cột Xem bài làm
    main.cell(header_row, col_link).value = "Xem bài làm"
    main.cell(header_row, col_link).font = Font(bold=True)
    main.cell(header_row, col_link).alignment = Alignment(horizontal="center")

    # Dọn cột thừa bên phải link (từ lần xuất trước)
    for c in range(col_link + 1, col_link + 6):
        if main.cell(header_row, c).value in (
            "Điểm TN (/100)",
            "Link xem dự án (.sb3)",
            "Link kết quả / ảnh TN",
            "Link xem dự án",
            "Link kết quả",
        ):
            for r in range(header_row, header_row + 20):
                main.cell(r, c).value = None
                main.cell(r, c).hyperlink = None

    used_titles = {main_title}
    ok_count = 0
    miss = []

    for st in roster["students"]:
        name = st["name"]
        row = st["row"]
        attempt = find_attempt(attempts, name, grade_keys)
        if not attempt:
            main.cell(row, col_score).value = "—"
            main.cell(row, col_link).value = "(chưa có bài)"
            main.cell(row, col_link).hyperlink = None
            miss.append(name)
            continue

        details = attempt.get("details") or []
        mc100, earned, max_pts, mc = mc_score_100(details)
        grade = (attempt.get("student_grade") or label).strip()

        # Điểm trên phiếu = chỉ TN
        main.cell(row, col_score).value = format_score(mc100)

        title = sheet_title_for(name, used_titles)
        write_student_sheet(wb, title, name, grade, mc100, earned, max_pts, mc, qmap)

        set_internal_sheet_link(main.cell(row, col_link), title, "Xem bài làm")
        ok_count += 1

    main.column_dimensions[get_column_letter(col_link)].width = 16

    # Cập nhật ghi chú: điểm trên phiếu = trắc nghiệm
    for r in range(1, (main.max_row or 1) + 1):
        v = main.cell(r, 1).value
        if isinstance(v, str) and v.startswith("Ghi chú:"):
            main.cell(r, 1).value = (
                "Ghi chú: Điểm trên phiếu là điểm trắc nghiệm (thang 100). "
                "Bấm «Xem bài làm» để mở sheet chi tiết từng câu (đáp án đúng / đáp án học sinh chọn). "
                "Phụ huynh vui lòng liên hệ giáo viên nếu cần trao đổi thêm về lộ trình học tập của em."
            )
            break

    wb.save(wb_path)
    return ok_count, miss, len(roster["students"])


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGODB_DB_NAME")]
    quiz = db.quizzes.find_one({"_id": ObjectId(QUIZ_ID)}) or db.quizzes.find_one({"_id": QUIZ_ID})
    if not quiz:
        print("QUIZ_NOT_FOUND")
        sys.exit(1)

    attempts = list(db.quiz_attempts.find({"quiz_id": str(quiz["_id"])}))
    qmap = quiz_mc_by_id(quiz)
    print(f"quiz={quiz.get('title')} attempts={len(attempts)} mc_questions={len(qmap)}")

    for cfg in CLASSES:
        path = os.path.join(KETQUA_DIR, cfg["file"])
        if not os.path.exists(path):
            print("MISSING_FILE", path)
            continue
        ok, miss, total = process_class(path, cfg["grade_keys"], cfg["label"], attempts, qmap)
        print(f"OK {cfg['file']}: matched={ok}/{total} miss={miss}")


if __name__ == "__main__":
    main()
