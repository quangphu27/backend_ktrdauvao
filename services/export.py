import io
from datetime import datetime
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def export_tests_excel(tests):
    wb = Workbook()
    ws = wb.active
    ws.title = "Ket qua kiem tra"
    headers = [
        "ID", "Học sinh", "Lớp", "Số điện thoại", "Khóa học", "Điểm", "Lộ trình",
        "Nhận xét", "Thời gian (giây)", "Ngày nộp",
    ]
    ws.append(headers)
    for t in tests:
        submitted = t.get("submitted_at")
        ws.append([
            t.get("id"),
            t.get("student_name"),
            t.get("student_grade"),
            t.get("student_phone"),
            t.get("course_name"),
            t.get("score"),
            t.get("recommendation"),
            t.get("comment"),
            t.get("duration_seconds"),
            submitted.strftime("%d/%m/%Y %H:%M") if submitted else "",
        ])
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def export_tests_pdf(tests):
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=landscape(A4), topMargin=1 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=16, spaceAfter=20)
    elements = [
        Paragraph("Bao cao ket qua kiem tra nang luc dau vao", title_style),
        Paragraph(f"Ngay xuat: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]),
        Spacer(1, 0.5 * cm),
    ]
    data = [["ID", "Hoc sinh", "Lop", "SDT", "Khoa hoc", "Diem", "Lo trinh", "Ngay nop"]]
    for t in tests:
        submitted = t.get("submitted_at")
        data.append([
            str(t.get("id")),
            t.get("student_name"),
            t.get("student_grade"),
            t.get("student_phone"),
            t.get("course_name"),
            f"{t.get('score')}",
            t.get("recommendation"),
            submitted.strftime("%d/%m/%Y") if submitted else "",
        ])
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4A90D9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F0F8FF")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#E8F4FD")]),
    ]))
    elements.append(table)
    doc.build(elements)
    output.seek(0)
    return output
