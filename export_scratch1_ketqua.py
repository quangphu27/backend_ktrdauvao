"""Xuất ảnh kết quả trắc nghiệm (/100) + cập nhật Excel phiếu nhận xét Scratch 1."""
from __future__ import annotations

import os
import re
import sys
from urllib.parse import quote

from bson import ObjectId
from dotenv import load_dotenv
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Font
from PIL import Image, ImageDraw, ImageFont
from pymongo import MongoClient

load_dotenv()

QUIZ_ID = "6ab7e539c4110429822a0cb0"
GRADE_KEYS = {"Scratch1", "Scratch 1"}
# Tên trên phiếu nhận xét (thứ tự giữ nguyên)
ROSTER = [
    "Dương Phúc Khang",
    "Nguyễn Hữu Tài",
    "Dương Đức Hiếu",
]

BACKEND = (os.getenv("BACKEND_URL") or "https://backend-ktrdauvao.onrender.com").rstrip("/")
FRONTEND = (os.getenv("FRONTEND_URL") or "https://kiemtradauvao.vercel.app").rstrip("/")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "frontend", "public", "ketqua", "scratch1")
XLSX_PATH = os.path.join(ROOT, "frontend", "public", "ketqua", "Scratch 1.xlsx")


def _fonts():
    bold = reg = None
    for b, r in (
        ("C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/segoeui.ttf"),
        ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"),
    ):
        if os.path.exists(b) and os.path.exists(r):
            bold, reg = b, r
            break
    if not bold:
        return ImageFont.load_default(), ImageFont.load_default(), ImageFont.load_default()
    return (
        ImageFont.truetype(bold, 28),
        ImageFont.truetype(bold, 18),
        ImageFont.truetype(reg, 14),
    )


def _wrap(text, font, max_w, draw):
    words = str(text or "").replace("\n", " ").split()
    if not words:
        return [""]
    lines, cur = [], words[0]
    for w in words[1:]:
        trial = f"{cur} {w}"
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def _abs_file_url(file_doc):
    if not file_doc:
        return ""
    url = (file_doc.get("url") or "").strip()
    if not url:
        return ""
    if url.startswith("/"):
        return BACKEND + url
    return url


def _slug(name: str) -> str:
    import unicodedata

    s = unicodedata.normalize("NFD", name.strip().lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("đ", "d")
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_\-]", "", s)
    return s or "hs"


def normalize_name(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def mc_score_100(details):
    mc = [d for d in details if d.get("type") == "mcq"]
    earned = sum(int(d.get("points_awarded") or 0) for d in mc)
    max_pts = sum(int(d.get("points") or 0) for d in mc)
    if max_pts <= 0:
        return 0.0, earned, max_pts, mc
    return round(earned / max_pts * 100, 1), earned, max_pts, mc


def render_mc_image(student_name, grade, total_score, mc100, earned, max_pts, mc_details, out_path):
    font_title, font_h, font_body = _fonts()
    width = 980
    pad = 28
    line_h = 22
    # estimate height
    rows_h = 0
    probe = Image.new("RGB", (width, 100), "white")
    pdraw = ImageDraw.Draw(probe)
    for d in mc_details:
        sa = d.get("student_answer") or "(trống)"
        ca = d.get("correct_answer") or "—"
        rows_h += 26  # header line
        for _ in _wrap(f"HS chọn: {sa}", font_body, width - pad * 2 - 40, pdraw):
            rows_h += line_h
        if not d.get("is_correct"):
            for _ in _wrap(f"Đáp án đúng: {ca}", font_body, width - pad * 2 - 40, pdraw):
                rows_h += line_h
        rows_h += 10

    height = 160 + rows_h + 40
    img = Image.new("RGB", (width, height), (248, 251, 255))
    draw = ImageDraw.Draw(img)

    # header bar
    draw.rectangle((0, 0, width, 120), fill=(30, 120, 200))
    draw.text((pad, 18), "KẾT QUẢ TRẮC NGHIỆM — thang 100", font=font_title, fill="white")
    draw.text((pad, 58), f"{student_name}  ·  {grade}", font=font_h, fill=(220, 240, 255))
    draw.text(
        (pad, 86),
        f"Điểm TN: {mc100}/100  ({earned}/{max_pts} raw)   |   Tổng bài (TN+dự án): {total_score}/100",
        font=font_body,
        fill=(255, 255, 255),
    )

    y = 140
    for i, d in enumerate(mc_details, 1):
        ok = bool(d.get("is_correct"))
        badge = "ĐÚNG" if ok else "SAI"
        color = (20, 140, 80) if ok else (200, 50, 50)
        bg = (225, 250, 235) if ok else (255, 235, 235)
        sa = d.get("student_answer") or "(trống)"
        ca = d.get("correct_answer") or "—"
        content = (d.get("content") or "").strip()
        # short content
        q_title = content.split("\n")[0][:90] if content else f"Câu {i}"

        block_lines = [f"Câu {i}. {badge}  —  {q_title}"]
        block_lines += _wrap(f"HS chọn: {sa}", font_body, width - pad * 2 - 36, draw)
        if not ok:
            block_lines += _wrap(f"Đáp án đúng: {ca}", font_body, width - pad * 2 - 36, draw)

        block_h = 8 + len(block_lines) * line_h + 8
        draw.rounded_rectangle((pad, y, width - pad, y + block_h), radius=10, fill=bg)
        draw.ellipse((pad + 10, y + 10, pad + 22, y + 22), fill=color)
        ty = y + 6
        for li, line in enumerate(block_lines):
            fill = color if li == 0 else (40, 50, 70)
            fnt = font_body if li else font_h
            # first line uses smaller bold-ish via font_h size mismatch — keep font_body for long
            draw.text((pad + 30, ty), line, font=font_body if li else font_h, fill=fill)
            ty += line_h
        y += block_h + 8

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    return out_path


def find_attempt(attempts, name):
    key = normalize_name(name)
    for a in attempts:
        if normalize_name(a.get("student_name") or "") == key and (
            (a.get("student_grade") or "").strip() in GRADE_KEYS
            or True
        ):
            # prefer Scratch1 grade match
            if (a.get("student_grade") or "").strip() in GRADE_KEYS:
                return a
    for a in attempts:
        if normalize_name(a.get("student_name") or "") == key:
            return a
    return None


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
    os.makedirs(OUT_DIR, exist_ok=True)

    rows = []
    for name in ROSTER:
        a = find_attempt(attempts, name)
        if not a:
            print("MISSING", name)
            continue
        details = a.get("details") or []
        mc100, earned, max_pts, mc = mc_score_100(details)
        sb = next((d for d in details if d.get("type") == "scratch_file"), None)
        file_url = _abs_file_url((sb or {}).get("file"))
        attempt_id = str(a["_id"])
        detail_url = f"{FRONTEND}/quiz-ket-qua/{attempt_id}"
        admin_url = f"{FRONTEND}/admin/quizzes/{QUIZ_ID}/results?attempt={attempt_id}"
        project_view = (
            f"https://turbowarp.org/embed?project_url={quote(file_url, safe='')}"
            if file_url
            else ""
        )
        img_name = f"{_slug(name)}_trac_nghiem.png"
        img_path = os.path.join(OUT_DIR, img_name)
        render_mc_image(
            name,
            a.get("student_grade") or "Scratch1",
            a.get("score"),
            mc100,
            earned,
            max_pts,
            mc,
            img_path,
        )
        public_img = f"/ketqua/scratch1/{img_name}"
        rows.append(
            {
                "name": name,
                "total": a.get("score"),
                "mc100": mc100,
                "earned_mc": earned,
                "max_mc": max_pts,
                "file_url": file_url,
                "project_view": project_view,
                "detail_url": detail_url,
                "admin_url": admin_url,
                "img_path": img_path,
                "public_img": public_img,
                "attempt_id": attempt_id,
            }
        )
        print(
            f"OK {name}: total={a.get('score')} MC={mc100}/100 ({earned}/{max_pts}) "
            f"sb3={'yes' if file_url else 'no'} img={img_path}"
        )

    # Cập nhật Excel: giữ phiếu nhận xét, thêm sheet chi tiết + cột link
    if not os.path.exists(XLSX_PATH):
        print("XLSX_MISSING", XLSX_PATH)
        sys.exit(1)

    wb = load_workbook(XLSX_PATH)
    ws = wb.active

    # Thêm header cột E, F, G nếu chưa có
    if (ws.cell(7, 5).value or "") != "Điểm TN (/100)":
        ws.cell(7, 5).value = "Điểm TN (/100)"
        ws.cell(7, 6).value = "Link xem dự án (.sb3)"
        ws.cell(7, 7).value = "Link kết quả / ảnh TN"
        for col in range(5, 8):
            ws.cell(7, col).font = Font(bold=True)

    by_name = {r["name"]: r for r in rows}
    link_font = Font(color="0563C1", underline="single")
    for row_idx in range(8, 20):
        name = ws.cell(row_idx, 2).value
        if not name or name not in by_name:
            continue
        r = by_name[name]
        # điểm tổng giữ nguyên nếu đã có; chuẩn hóa dạng x/100
        ws.cell(row_idx, 3).value = f"{int(r['total']) if float(r['total']) == int(r['total']) else r['total']}/100"
        ws.cell(row_idx, 5).value = f"{r['mc100']}/100"
        c_proj = ws.cell(row_idx, 6)
        if r["file_url"]:
            c_proj.value = "Xem dự án trên web"
            c_proj.hyperlink = r["admin_url"]  # admin có TurboWarp embed
            c_proj.font = link_font
        else:
            c_proj.value = "(chưa nộp)"
        c_res = ws.cell(row_idx, 7)
        c_res.value = "Xem kết quả + ảnh TN"
        # link tới trang kết quả công khai; ảnh nằm trên site
        c_res.hyperlink = r["detail_url"]
        c_res.font = link_font

    ws.column_dimensions["E"].width = 16
    ws.column_dimensions["F"].width = 24
    ws.column_dimensions["G"].width = 24

    # Sheet chi tiết
    if "Chi_tiet_TN" in wb.sheetnames:
        del wb["Chi_tiet_TN"]
    detail = wb.create_sheet("Chi_tiet_TN")
    headers = [
        "STT",
        "Họ và tên",
        "Điểm tổng /100",
        "Điểm TN /100",
        "TN raw",
        "Link xem dự án (TurboWarp)",
        "Link file .sb3",
        "Link chi tiết bài",
        "Link admin",
        "Ảnh kết quả TN (path)",
    ]
    detail.append(headers)
    for cell in detail[1]:
        cell.font = Font(bold=True)
    for i, r in enumerate(rows, 1):
        detail.append(
            [
                i,
                r["name"],
                r["total"],
                r["mc100"],
                f"{r['earned_mc']}/{r['max_mc']}",
                "Mở TurboWarp",
                "Tải / mở .sb3",
                "Xem chi tiết",
                "Admin chấm bài",
                r["public_img"],
            ]
        )
        row = detail.max_row
        if r["project_view"]:
            detail.cell(row, 6).hyperlink = r["project_view"]
            detail.cell(row, 6).font = link_font
        if r["file_url"]:
            detail.cell(row, 7).hyperlink = r["file_url"]
            detail.cell(row, 7).font = link_font
        detail.cell(row, 8).hyperlink = r["detail_url"]
        detail.cell(row, 8).font = link_font
        detail.cell(row, 9).hyperlink = r["admin_url"]
        detail.cell(row, 9).font = link_font

    # Sheet ảnh (embed thumbnail nhỏ + full path)
    if "Anh_TN" in wb.sheetnames:
        del wb["Anh_TN"]
    img_sheet = wb.create_sheet("Anh_TN")
    img_sheet["A1"] = "Ảnh kết quả trắc nghiệm từng học sinh (thang 100)"
    img_sheet["A1"].font = Font(bold=True, size=14)
    y_anchor = 3
    for r in rows:
        img_sheet.cell(y_anchor, 1).value = r["name"]
        img_sheet.cell(y_anchor, 1).font = Font(bold=True)
        img_sheet.cell(y_anchor + 1, 1).value = f"Điểm TN: {r['mc100']}/100 | Tổng: {r['total']}/100"
        if r["file_url"]:
            cell = img_sheet.cell(y_anchor + 2, 1)
            cell.value = "Link xem dự án"
            cell.hyperlink = r["admin_url"]
            cell.font = link_font
        try:
            xl_img = XLImage(r["img_path"])
            # scale width ~480px
            ratio = 480 / float(xl_img.width)
            xl_img.width = 480
            xl_img.height = int(xl_img.height * ratio)
            img_sheet.add_image(xl_img, f"A{y_anchor + 4}")
            # rough row advance by image height
            y_anchor += 4 + max(20, int(xl_img.height / 15)) + 2
        except Exception as exc:
            img_sheet.cell(y_anchor + 4, 1).value = f"(không nhúng được ảnh: {exc})"
            y_anchor += 8

    wb.save(XLSX_PATH)
    print(f"UPDATED_XLSX {XLSX_PATH}")
    print(f"IMAGES_DIR {OUT_DIR}")
    print(f"STUDENTS {len(rows)}")


if __name__ == "__main__":
    main()
