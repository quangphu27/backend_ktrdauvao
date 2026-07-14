"""Ảnh phản hồi kiểm tra — layout động, chữ đậm, giao diện vui cho trẻ."""

import math
import os
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from services.scoring import CATEGORY_MAP
from services.class_assignment import (
    filter_study_roadmap,
    format_display_name,
    get_class_info,
    get_scratch_class_roadmap,
)

ASSETS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "feedback")

# Màu tươi — thân thiện trẻ em
C_BLUE = (30, 100, 200)
C_BLUE_DARK = (20, 70, 160)
C_SKY = (220, 240, 255)
C_CREAM = (255, 252, 245)
C_WHITE = (255, 255, 255)
C_TEXT = (25, 35, 55)
C_MUTED = (80, 95, 115)
C_GOLD = (255, 180, 0)
C_GREEN = (30, 160, 90)
C_ORANGE = (255, 140, 40)
C_RED = (220, 60, 60)
C_PINK = (255, 120, 150)
C_PURPLE = (140, 90, 220)
C_BORDER = (180, 210, 245)
C_GREEN_BG = (225, 250, 235)
C_ORANGE_BG = (255, 242, 225)
C_YELLOW_BG = (255, 250, 220)

SKILL_LEFT_W = 210
PAD_BOTTOM = 8
FOOTER_H = 36

RADAR_VI = {
    "Logic": "Tư duy logic",
    "Creative": "Quan sát",
    "Math": "Tính toán",
    "Algorithm": "Thuật toán",
    "Memory": "Đọc hiểu code",
}
SCRATCH_RADAR_VI = {
    "Logic": "Tư duy logic",
    "Creative": "Quan sát",
    "Math": "Tính toán",
    "Algorithm": "Thuật toán / Vòng lặp",
    "Memory": "Phân tích khối lệnh",
}
CATEGORY_VI = {
    "logic": "tư duy logic",
    "observation": "quan sát",
    "problem_solving": "giải quyết vấn đề",
    "sequencing": "sắp xếp khối lệnh",
    "memory": "đọc hiểu code",
    "math": "tính toán",
    "algorithm": "thuật toán",
}


def _asset(name):
    p = os.path.join(ASSETS, name)
    return p if os.path.exists(p) else None


def _fonts():
    bold, reg = None, None
    for b, r in (
        ("C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/segoeui.ttf"),
        ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"),
    ):
        if os.path.exists(b) and os.path.exists(r):
            bold, reg = b, r
            break
    if not bold:
        d = ImageFont.load_default()
        return {k: d for k in ("brand", "title", "h1", "h2", "body", "small")}
    return {
        "brand": ImageFont.truetype(bold, 30),
        "title": ImageFont.truetype(bold, 34),
        "h1": ImageFont.truetype(bold, 22),
        "h2": ImageFont.truetype(bold, 18),
        "body": ImageFont.truetype(bold, 15),
        "small": ImageFont.truetype(bold, 13),
    }


def _star_points(cx, cy, outer_r, inner_r=None):
    if inner_r is None:
        inner_r = outer_r * 0.42
    return [
        (cx + (outer_r if i % 2 == 0 else inner_r) * math.cos(math.pi / 2 + i * math.pi / 5),
         cy - (outer_r if i % 2 == 0 else inner_r) * math.sin(math.pi / 2 + i * math.pi / 5))
        for i in range(10)
    ]


def _draw_stars(draw, x, y, count, total=5):
    """Vẽ sao bằng polygon — tránh lỗi font emoji/unicode."""
    n = max(0, min(total, int(count)))
    size, gap = 12, 28
    for i in range(total):
        cx = x + i * gap + size
        cy = y + size
        pts = _star_points(cx, cy, size)
        if i < n:
            draw.polygon(pts, fill=C_GOLD, outline=(210, 150, 0))
        else:
            draw.polygon(pts, outline=(200, 170, 80), width=2)
    return size * 2 + 10


def _lh(font, extra=6):
    return font.size + extra


def _stars_from_wrong(wrong_count):
    """5 sao gốc — sai 1–2 câu trừ 1 sao, sai 3–4 câu trừ thêm 1 sao."""
    w = max(0, int(wrong_count))
    if w == 0:
        return 5
    deduct = 1 + (w - 1) // 2
    return max(1, 5 - deduct)


def _score_stars(pct):
    """Sao tổng quan theo điểm % (phần đánh giá chung)."""
    if pct >= 90:
        return 5
    if pct >= 75:
        return 4
    if pct >= 60:
        return 3
    if pct >= 40:
        return 2
    return 1


def _wrap(text, font, max_w, draw):
    if not text:
        return []
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = f"{cur} {w}".strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _rating_label(score):
    if score >= 90:
        return "Rất tốt / Excellent", 5, C_GREEN
    if score >= 75:
        return "Tốt / Good", 4, C_GREEN
    if score >= 60:
        return "Khá / Fair", 3, C_BLUE
    if score >= 40:
        return "Trung bình / Average", 2, C_ORANGE
    return "Cần cải thiện / Needs work", 1, C_RED


def _rating_word(stars):
    return ["", "Yếu", "TB", "Khá", "Tốt", "Rất tốt"][stars]


def _clean_q(content, n=70):
    if not content:
        return ""
    t = content.replace("`", "").replace("\n", " ").strip()
    while "  " in t:
        t = t.replace("  ", " ")
    return t if len(t) <= n else t[: n - 3] + "..."


def _map_radar_stats(cat_stats):
    out = {}
    for cat, s in cat_stats.items():
        key = CATEGORY_MAP.get(cat, "Logic")
        out.setdefault(key, {"ok": 0, "total": 0, "wrong": []})
        out[key]["ok"] += s["ok"]
        out[key]["total"] += s["total"]
        out[key]["wrong"].extend(s.get("wrong", []))
    return out


def _analyze_full(details):
    cat_stats = {}
    level_stats = {
        "easy": {"ok": 0, "total": 0},
        "medium": {"ok": 0, "total": 0},
        "hard": {"ok": 0, "total": 0},
    }
    wrong_all, unanswered = [], []
    for d in details or []:
        cat = d.get("category") or "logic"
        cat_stats.setdefault(cat, {"ok": 0, "total": 0, "wrong": []})
        cat_stats[cat]["total"] += 1
        lv = d.get("level") or "medium"
        if lv in level_stats:
            level_stats[lv]["total"] += 1
        if d.get("is_correct"):
            cat_stats[cat]["ok"] += 1
            if lv in level_stats:
                level_stats[lv]["ok"] += 1
        else:
            item = {
                "q": _clean_q(d.get("question_content")),
                "chosen": d.get("answer_text") or "",
                "correct": d.get("correct_answer") or "",
                "cat": cat,
                "level": lv,
            }
            cat_stats[cat]["wrong"].append(item)
            wrong_all.append(item)
            if not d.get("answer_text"):
                unanswered.append(item)
    return {
        "cat_stats": cat_stats,
        "level_stats": level_stats,
        "wrong_all": wrong_all,
        "unanswered": unanswered,
    }


def _skill_tip(name, course, pct):
    is_scratch = (course or "").lower() == "scratch"
    unit = "khối lệnh" if is_scratch else "dòng code"
    low = name.lower()
    if "logic" in low:
        return (
            "Em nên tập suy nghĩ «nếu… thì…» khi đọc đề, rồi mới quyết định chọn đáp án."
            if pct < 0.65
            else "Tiếp tục rèn tư duy bằng các bài đố vui logic trên Scratch."
            if is_scratch
            else "Tiếp tục luyện đọc hiểu kết quả in ra từng dòng code."
        )
    if "quan sát" in low:
        return (
            "Hãy nhìn kỹ hình minh họa và mô tả tình huống trước khi chọn — đừng vội."
            if pct < 0.65
            else "Duy trì thói quen quan sát chi tiết, em sẽ ít bị nhầm hơn."
        )
    if "tính toán" in low:
        return (
            "Luyện tính nhẩm số lần lặp, số bước di chuyển trước khi chạy thử chương trình."
            if pct < 0.65
            else "Phần tính toán em khá vững — có thể thử các bài đếm phức tạp hơn."
        )
    if "thuật toán" in low or "vòng lặp" in low:
        return (
            f"Ôn lại cách dùng vòng lặp và điều kiện qua các {unit} mẫu ngắn mỗi ngày."
            if pct < 0.65
            else "Thử ghép vòng lặp với điều kiện trong một mini-project nhỏ."
        )
    if "khối lệnh" in low or "đọc hiểu" in low:
        return (
            f"Tập trace từng {unit} bằng tay, hình dung chương trình chạy từng bước một."
            if pct < 0.65
            else f"Thử đọc các chương trình dài hơn và tự giải thích từng {unit}."
        )
    return (
        f"Nên luyện đều phần này trên máy tính, mỗi buổi 15–20 phút là đủ thấy tiến bộ."
    )


def _skill_comment(name, ok, total, wrong_samples, course):
    """3–4 câu nhận xét tự nhiên theo chi tiết bài làm."""
    wrong_count = total - ok
    stars = _stars_from_wrong(wrong_count)
    unit = "khối lệnh" if (course or "").lower() == "scratch" else "dòng code"
    wrong = wrong_samples or []
    blanks = [w for w in wrong if not w.get("chosen")]
    easy_w = [w for w in wrong if w.get("level") == "easy"]
    hard_w = [w for w in wrong if w.get("level") == "hard"]
    sentences = []

    if wrong_count == 0:
        sentences.append(
            f"Em trả lời đúng cả {total} câu — cho thấy em đã nắm khá vững kỹ năng này."
        )
    elif wrong_count <= 2:
        sentences.append(
            f"Em đúng {ok}/{total} câu, mắc {wrong_count} câu — "
            f"nhìn chung vẫn ổn nhưng cần cẩn thận hơn một chút."
        )
    elif wrong_count <= 4:
        sentences.append(
            f"Em đúng {ok}/{total} câu — còn {wrong_count} câu chưa chính xác, "
            f"nên dành thêm thời gian ôn luyện."
        )
    else:
        sentences.append(
            f"Em mới đúng {ok}/{total} câu — phần này em cần được hướng dẫn và luyện thêm."
        )

    if not wrong:
        sentences.append(f"Em đã quen cách đọc và suy luận qua từng {unit}.")
    elif blanks:
        sentences.append(
            f"Có {len(blanks)} câu chưa trả lời — em hãy đọc hết đề rồi thử chọn trước khi bỏ qua."
        )
    elif easy_w and len(easy_w) >= len(hard_w):
        sentences.append(
            f"Em còn vướng ở vài câu cơ bản — nên đọc chậm từng {unit} rồi mới chọn đáp án."
        )
    elif hard_w:
        sentences.append(
            "Các câu khó hơn em gặp khó — ôn lại nền tảng rồi luyện dần sẽ dễ hơn."
        )
    else:
        sentences.append("Em cố gắng rồi — luyện thêm vài buổi là sẽ tự tin hơn.")

    sentences.append(_skill_tip(name, course, ok / total if total else 0))

    if wrong_count <= 2:
        sentences.append("Giữ nhịp học đều, em sẽ ít mắc lỗi tương tự trong các bài sau.")
    else:
        sentences.append("Đừng nản, học từng bước nhỏ mỗi ngày em sẽ thấy tiến bộ rõ ràng.")

    return " ".join(sentences[:4])


def _strengths_weaknesses(cat_stats):
    strong, weak = [], []
    for cat, s in cat_stats.items():
        if not s["total"]:
            continue
        label = CATEGORY_VI.get(cat, cat)
        ratio = s["ok"] / s["total"]
        txt = f"{label} ({s['ok']}/{s['total']} câu)"
        if ratio >= 0.75:
            strong.append(txt)
        elif ratio < 0.6:
            weak.append(txt)
    if not strong:
        strong.append("Tham gia kiểm tra nhiệt tình, sẵn sàng học thêm")
    if not weak:
        weak.append("Đọc kỹ đề và kiểm tra lại trước khi nộp bài")
    return strong[:5], weak[:5]


def _skill_ratio(sk):
    a, b = sk["score_text"].split("/")
    return int(a) / max(1, int(b))


def _is_scratch(course):
    return (course or "").lower() == "scratch"


def _scratch_assessment_notes(score, course):
    """Scratch: <60 chưa có kiến thức; <50 chưa thành thạo máy tính."""
    if not _is_scratch(course):
        return []
    notes = []
    if score < 50:
        notes.append("Chưa thành thạo máy tính")
    if score < 60:
        notes.append("Chưa có kiến thức Scratch")
    return notes


def _scratch_teacher_comment(name, score, correct, total, analysis, recommendation):
    """Nhận xét giáo viên riêng cho Scratch dưới 60 điểm."""
    sentences = [
        f"Em {name} đạt {score} điểm với {correct}/{total} câu đúng trong bài kiểm tra Scratch."
    ]
    if score < 50:
        sentences.append(
            "Em cần làm quen thêm với chuột, bàn phím và thao tác cơ bản trên máy tính."
        )
        sentences.append(
            "Kiến thức Scratch như khối lệnh, sự kiện em cũng cần được hướng dẫn từ đầu."
        )
    else:
        sentences.append(
            "Em đã biết thao tác máy ở mức cơ bản nhưng chưa vững kiến thức Scratch."
        )
        sentences.append(
            "Khối lệnh, vòng lặp và sắp xếp thứ tự là phần em nên học từng bước."
        )

    if analysis["unanswered"]:
        sentences.append(
            f"Em bỏ trống {len(analysis['unanswered'])} câu — lần sau cứ thử chọn hết nhé."
        )
    else:
        sentences.append("Em đã cố gắng trả lời hầu hết các câu — đó là điểm đáng khen.")

    if recommendation:
        sentences.append(f"Thầy xếp em vào {recommendation}, em tham gia đều các buổi học nhé.")

    sentences.append(
        f"Thầy tin em {name} sẽ tiến bộ nếu kiên trì luyện tập trên máy tính mỗi tuần."
    )
    return " ".join(sentences[:7])


def _teacher_comment(test, analysis, score, course, skills):
    """6–7 câu nhận xét giáo viên — tự nhiên, không lặp ý."""
    name = format_display_name(test.get("student_name"), test.get("student_phone"))
    correct = sum(1 for d in (test.get("details") or []) if d.get("is_correct"))
    total = len(test.get("details") or [])
    recommendation = test.get("recommendation") or ""

    if _is_scratch(course) and score < 60:
        return _scratch_teacher_comment(
            name, score, correct, total, analysis, recommendation
        )

    unit = "khối lệnh" if course.lower() == "scratch" else "dòng code"
    sentences = []

    if score >= 75:
        sentences.append(
            f"Em {name} làm bài {course} khá tốt — {score} điểm, {correct}/{total} câu đúng."
        )
    elif score >= 60:
        sentences.append(
            f"Em {name} đạt {score} điểm ({correct}/{total} câu đúng) — kết quả khá, còn dư địa tiến bộ."
        )
    else:
        sentences.append(
            f"Em {name} đạt {score} điểm ({correct}/{total} câu đúng) — cần luyện thêm để vững hơn."
        )

    if skills:
        best = max(skills, key=_skill_ratio)
        worst = min(skills, key=_skill_ratio)
        if _skill_ratio(best) >= 0.75:
            sentences.append(
                f"Em thể hiện tốt nhất ở {best['name'].lower()} ({best['score_text']})."
            )
        if worst["name"] != best["name"] and _skill_ratio(worst) < 0.65:
            sentences.append(
                f"Nên ưu tiên ôn {worst['name'].lower()} ({worst['score_text']}) trước."
            )

    unanswered = analysis["unanswered"]
    if unanswered:
        sentences.append(
            f"Em bỏ trống {len(unanswered)} câu — lần sau hãy thử trả lời hết nhé."
        )
    elif score < 70:
        sentences.append(
            f"Em nên đọc kỹ từng {unit} trước khi chọn, tránh vội vàng."
        )
    else:
        sentences.append("Thói quen đọc đề cẩn thận của em là điểm cộng đáng giữ.")

    if recommendation:
        sentences.append(f"Thầy xếp em vào {recommendation} — em cố gắng tham gia đều các buổi học.")

    sentences.append(
        f"Thầy tin em {name} sẽ tiến bộ rõ rệt nếu kiên trì thực hành mỗi tuần."
    )

    return " ".join(sentences[:7])


def _parse_comment(comment):
    remark, roadmap = "", []
    if not comment:
        return remark, roadmap
    for block in comment.split("\n\n"):
        if block.startswith("Nhận xét chung"):
            remark = block.replace("Nhận xét chung", "", 1).strip()
        elif block.startswith("Đề xuất lộ trình"):
            for line in block.split("\n"):
                line = line.strip()
                if line.startswith("•"):
                    roadmap.append(line[1:].strip())
    return remark, roadmap


def build_feedback_data(test, comment=""):
    course = test.get("course_name") or ""
    score = float(test.get("score") or 0)
    details = test.get("details") or []
    is_scratch = course.lower() == "scratch"
    radar_map = SCRATCH_RADAR_VI if is_scratch else RADAR_VI

    analysis = _analyze_full(details)
    cat_stats = analysis["cat_stats"]
    radar_stats = _map_radar_stats(cat_stats)
    strong, weak = _strengths_weaknesses(cat_stats)
    remark, roadmap = _parse_comment(comment)
    class_info = get_class_info(
        course, test.get("student_phone"), test.get("student_name"), score
    )
    class_schedule = class_info.get("schedule") or ""
    display_name = format_display_name(test.get("student_name"), test.get("student_phone"))
    if is_scratch:
        roadmap = get_scratch_class_roadmap(class_info.get("class_id", 3))
    else:
        roadmap = filter_study_roadmap(
            roadmap, test.get("recommendation") or class_info.get("name"), class_schedule
        )

    correct = sum(1 for d in details if d.get("is_correct"))
    total = len(details) or 30

    skills = []
    for key, vi_name in radar_map.items():
        rs = radar_stats.get(key, {"ok": 0, "total": 0, "wrong": []})
        ok, t = rs["ok"], rs["total"]
        if not t:
            continue
        wrong_count = t - ok
        stars = _stars_from_wrong(wrong_count)
        skills.append({
            "name": vi_name,
            "stars": stars,
            "score_text": f"{ok}/{t}",
            "rating": _rating_word(stars),
            "comment": _skill_comment(vi_name, ok, t, rs["wrong"], course),
        })

    rating_label, overall_stars, rating_color = _rating_label(score)
    lv = analysis["level_stats"]

    imbalance = ""
    if skills and max(s["stars"] for s in skills) - min(s["stars"] for s in skills) >= 2:
        imbalance = "Có sự chênh lệch giữa các kỹ năng"

    submitted = test.get("submitted_at") or ""
    if submitted and "T" in str(submitted):
        try:
            submitted = datetime.fromisoformat(str(submitted).replace("Z", "")).strftime("%d/%m/%Y")
        except ValueError:
            submitted = str(submitted)[:10]

    return {
        "student_name": display_name,
        "grade": test.get("student_grade") or "—",
        "course": course,
        "score": score,
        "correct": correct,
        "total": total,
        "rating_label": rating_label,
        "overall_stars": overall_stars,
        "rating_color": rating_color,
        "imbalance": imbalance,
        "recommendation": test.get("recommendation") or "",
        "scratch_notes": _scratch_assessment_notes(score, course),
        "skills": skills,
        "strengths": strong,
        "weaknesses": weak,
        "teacher_comment": _teacher_comment(
            test, analysis, score, course, skills
        ),
        "roadmap": roadmap,
        "class_schedule": class_schedule,
        "submitted": submitted,
        "is_scratch": is_scratch,
    }


def _paste_rgba(base, path, xy, max_size):
    if not path:
        return (0, 0)
    try:
        im = Image.open(path).convert("RGBA")
        im.thumbnail(max_size, Image.Resampling.LANCZOS)
        base.paste(im, xy, im)
        return im.size
    except OSError:
        return (0, 0)


def _dots(draw, x, y, w, h, color=(255, 220, 100)):
    for i in range(0, w, 28):
        for j in range(0, h, 28):
            draw.ellipse([x + i, y + j, x + i + 6, y + j + 6], fill=color)


def _section_bar(draw, x, y, w, num, title, fonts, color=C_BLUE):
    draw.rounded_rectangle([x, y, x + w, y + 42], radius=14, fill=color)
    draw.ellipse([x + 12, y + 8, x + 38, y + 34], fill=C_GOLD)
    draw.text((x + 18, y + 10), str(num), fill=C_WHITE, font=fonts["h2"])
    draw.text((x + 48, y + 11), title.upper(), fill=C_WHITE, font=fonts["h2"])
    return y + 54


def _card(draw, x, y, w, h, fill=C_WHITE, border=C_BORDER):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=fill, outline=border, width=2)


def _skill_card_metrics(sk, fonts, content_w, draw):
    """Trái: sao + điểm | Phải: nhận xét — tính chiều cao khớp khi vẽ."""
    comment_w = content_w - SKILL_LEFT_W - 44
    lines = _wrap(sk["comment"], fonts["small"], comment_w, draw)
    star_block = 34 + _lh(fonts["small"]) * 2 + 8
    row_h = max(star_block, len(lines) * _lh(fonts["small"]) + PAD_BOTTOM)
    total = 12 + _lh(fonts["h2"]) + row_h + 24
    return lines, max(total, 112)


def _overall_card_h(data, fonts, draw, content_w):
    """Chiều cao khối tổng quan — theo ghi chú Scratch."""
    left_h = 16 + _lh(fonts["h2"]) + 34 + _lh(fonts["body"]) + 8
    if data.get("imbalance"):
        left_h += _lh(fonts["small"]) + 4

    right_w = content_w - 360
    right_h = 30 + _lh(fonts["body"]) + 8
    for note in data.get("scratch_notes") or []:
        for ln in _wrap(f"• {note}", fonts["small"], right_w, draw):
            right_h += _lh(fonts["small"])
    return max(120, left_h, right_h + 20) + 24


def _roadmap_metrics(data, fonts, draw, content_w):
    items = data["roadmap"] or ["Luyện tập 2–3 buổi/tuần trên máy tính."]
    lines = []
    wrap_w = content_w - 140
    for item in items[:5]:
        lines.extend(_wrap("• " + item, fonts["body"], wrap_w, draw))
    header_h = 46
    if data.get("class_schedule"):
        for ln in _wrap(data["class_schedule"], fonts["small"], wrap_w, draw):
            header_h += _lh(fonts["small"])
        header_h += 6
    h = header_h + len(lines) * _lh(fonts["body"]) + 20
    return lines, max(h, 90)


def _compute_layout(data, fonts, W, pad):
    """Tính chiều cao từng khối trước khi vẽ — tránh cắt/đè chữ."""
    tmp = Image.new("RGB", (W, 200), C_WHITE)
    draw = ImageDraw.Draw(tmp)
    content_w = W - 2 * pad
    text_w = content_w - 40
    skill_w = content_w - SKILL_LEFT_W - 44
    teacher_w = content_w - 48
    col_w = (content_w - 16) // 2

    layout = {"sections": [], "total_h": 0}
    y = 20

    y += 130  # header
    y += 88   # student info

    # overall
    overall_h = _overall_card_h(data, fonts, draw, content_w)
    y += 54 + overall_h

    # skills
    y += 54
    skill_heights = []
    skill_lines = []
    for sk in data["skills"]:
        lines, h = _skill_card_metrics(sk, fonts, content_w, draw)
        skill_lines.append(lines)
        skill_heights.append(h)
        y += h + 12
    y += 8

    # strengths
    y += 54
    sw_wrap_w = col_w - 36
    s_lines = []
    for s in data["strengths"][:4]:
        s_lines.extend(_wrap("• " + s, fonts["small"], sw_wrap_w, draw))
    w_lines = []
    for w in data["weaknesses"][:4]:
        w_lines.extend(_wrap("• " + w, fonts["small"], sw_wrap_w, draw))
    sw_h = max(100, 48 + max(len(s_lines), len(w_lines)) * _lh(fonts["small"]) + 20)
    y += sw_h + 16

    # teacher
    y += 54
    tc = _wrap(data["teacher_comment"], fonts["body"], teacher_w, draw)
    t_h = max(100, 40 + len(tc) * _lh(fonts["body"]) + 24)
    y += t_h + 16

    # roadmap
    y += 54
    roadmap_lines, r_h = _roadmap_metrics(data, fonts, draw, content_w)
    y += r_h + 16 + FOOTER_H

    layout["total_h"] = y
    layout["overall_h"] = overall_h
    layout["skill_heights"] = skill_heights
    layout["skill_lines"] = skill_lines
    layout["sw_h"] = sw_h
    layout["teacher_h"] = t_h
    layout["teacher_lines"] = tc
    layout["roadmap_h"] = r_h
    layout["roadmap_lines"] = roadmap_lines
    layout["text_w"] = text_w
    layout["skill_w"] = skill_w
    layout["teacher_w"] = teacher_w
    layout["col_w"] = col_w
    return layout


def render_feedback_card(data, output_path, brand="Creative English Center"):
    W = 1200
    pad = 40
    fonts = _fonts()
    layout = _compute_layout(data, fonts, W, pad)
    H = layout["total_h"]
    content_w = W - 2 * pad

    img = Image.new("RGB", (W, H), C_CREAM)
    draw = ImageDraw.Draw(img)
    _dots(draw, 0, 0, W, H, (255, 235, 200))

    y = 20

    # ── Header ──
    _card(draw, pad, y, content_w, 120, fill=C_WHITE, border=C_BLUE)
    draw.rounded_rectangle([pad, y, pad + content_w, y + 8], radius=14, fill=C_ORANGE)
    logo = _asset("logo.png")
    if logo:
        _paste_rgba(img, logo, (pad + 18, y + 18), (95, 95))
    draw.text((pad + 125, y + 22), brand, fill=C_BLUE_DARK, font=fonts["brand"])
    draw.text((pad + 125, y + 54), "PHẢN HỒI BÀI KIỂM TRA", fill=C_BLUE, font=fonts["title"])
    draw.text((pad + 125, y + 92), "Báo cáo kiểm tra năng lực lập trình", fill=C_MUTED, font=fonts["small"])
    ci = _asset("scratch.png" if data["is_scratch"] else "python.png")
    if ci:
        _paste_rgba(img, ci, (W - pad - 125, y + 12), (108, 100))
    y += 130

    # ── Student ──
    _card(draw, pad, y, content_w, 78, fill=C_YELLOW_BG, border=C_GOLD)
    draw.text((pad + 22, y + 14), f"Học sinh: {data['student_name']}", fill=C_TEXT, font=fonts["h1"])
    draw.text(
        (pad + 22, y + 42),
        f"Lớp: {data['grade']}  |  Khóa: {data['course']}  |  Nộp: {data['submitted'] or '—'}",
        fill=C_MUTED,
        font=fonts["small"],
    )
    draw.text(
        (pad + 22, y + 60),
        f"Bài trắc nghiệm {data['total']} câu — {data['course']}",
        fill=C_MUTED,
        font=fonts["small"],
    )
    y += 88

    # ── 1. Overall ──
    y = _section_bar(draw, pad, y, content_w, 1, "Kết quả tổng quan", fonts, C_BLUE)
    bh = layout["overall_h"]
    _card(draw, pad, y, content_w, bh, fill=C_SKY)
    ox = pad + 24
    oy = y + 16
    right_w = content_w - 360

    draw.text((ox, oy), "ĐÁNH GIÁ CHUNG", fill=C_BLUE_DARK, font=fonts["h2"])
    star_h = _draw_stars(draw, ox, oy + 28, data["overall_stars"])
    draw.text((ox, oy + 28 + star_h), data["rating_label"], fill=data["rating_color"], font=fonts["body"])
    if data["imbalance"]:
        draw.text((ox, oy + 28 + star_h + _lh(fonts["body"])), data["imbalance"], fill=C_ORANGE, font=fonts["small"])

    sx = pad + 340
    draw.text((sx, oy), f"Điểm: {data['score']}/100", fill=C_TEXT, font=fonts["h1"])
    draw.text((sx, oy + 30), f"Đúng: {data['correct']}/{data['total']} câu", fill=C_TEXT, font=fonts["body"])
    note_y = oy + 54
    for note in data.get("scratch_notes") or []:
        for ln in _wrap(f"• {note}", fonts["small"], right_w, draw):
            draw.text((sx, note_y), ln, fill=C_ORANGE, font=fonts["small"])
            note_y += _lh(fonts["small"])

    mascot = _asset("mascot_happy.png") if data["score"] >= 75 else _asset("mascot_learn.png")
    if mascot:
        _paste_rgba(img, mascot, (W - pad - 175, y + 12), (155, 145))
    y += bh + 14

    # ── 2. Skills (sao trái — nhận xét phải) ──
    y = _section_bar(draw, pad, y, content_w, 2, "Đánh giá kỹ năng", fonts, C_PURPLE)
    comment_x = pad + 22 + SKILL_LEFT_W
    for i, sk in enumerate(data["skills"]):
        sh = layout["skill_heights"][i]
        lines = layout["skill_lines"][i]
        fill = C_WHITE if i % 2 == 0 else (245, 250, 255)
        _card(draw, pad, y, content_w, sh, fill=fill)
        ix = pad + 22
        draw.text((ix, y + 12), sk["name"], fill=C_BLUE, font=fonts["h2"])
        row_y = y + 12 + _lh(fonts["h2"]) + 8
        draw.line(
            [(comment_x - 10, row_y - 4), (comment_x - 10, y + sh - 14)],
            fill=C_BORDER,
            width=2,
        )
        star_h = _draw_stars(draw, ix, row_y, sk["stars"])
        draw.text((ix, row_y + star_h + 4), sk["rating"], fill=C_TEXT, font=fonts["small"])
        draw.text(
            (ix, row_y + star_h + 4 + _lh(fonts["small"])),
            sk["score_text"] + " câu",
            fill=C_MUTED,
            font=fonts["small"],
        )
        ty = row_y
        for ln in lines:
            draw.text((comment_x, ty), ln, fill=C_TEXT, font=fonts["small"])
            ty += _lh(fonts["small"])
        y += sh + 12
    y += 6

    # ── 3. Strengths / Weaknesses ──
    y = _section_bar(draw, pad, y, content_w, 3, "Điểm mạnh & Cần phát triển", fonts, C_GREEN)
    cw = layout["col_w"]
    sh = layout["sw_h"]
    _card(draw, pad, y, cw, sh, fill=C_GREEN_BG, border=C_GREEN)
    _card(draw, pad + cw + 16, y, cw, sh, fill=C_ORANGE_BG, border=C_ORANGE)
    draw.text((pad + 18, y + 12), "Điểm mạnh", fill=C_GREEN, font=fonts["h2"])
    draw.text((pad + cw + 34, y + 12), "Cần phát triển", fill=C_ORANGE, font=fonts["h2"])
    sy = y + 40
    for s in data["strengths"][:4]:
        for ln in _wrap("• " + s, fonts["small"], cw - 36, draw):
            draw.text((pad + 16, sy), ln, fill=C_TEXT, font=fonts["small"])
            sy += _lh(fonts["small"])
    wy = y + 40
    for w in data["weaknesses"][:4]:
        for ln in _wrap("• " + w, fonts["small"], cw - 36, draw):
            draw.text((pad + cw + 32, wy), ln, fill=C_TEXT, font=fonts["small"])
            wy += _lh(fonts["small"])
    y += sh + 16

    # ── 4. Teacher (full width text, mascot below-right corner outside text flow) ──
    y = _section_bar(draw, pad, y, content_w, 4, "Nhận xét của giáo viên", fonts, C_ORANGE)
    th = layout["teacher_h"]
    _card(draw, pad, y, content_w, th, fill=C_WHITE, border=C_ORANGE)
    ty = y + 18
    for ln in layout["teacher_lines"]:
        draw.text((pad + 22, ty), ln, fill=C_TEXT, font=fonts["body"])
        ty += _lh(fonts["body"])
    y += th + 16

    # ── 5. Roadmap ──
    y = _section_bar(draw, pad, y, content_w, 5, "Lộ trình đề xuất", fonts, C_BLUE)
    rh = layout["roadmap_h"]
    _card(draw, pad, y, content_w, rh, fill=C_YELLOW_BG, border=C_GOLD)
    draw.text((pad + 22, y + 14), data["recommendation"], fill=C_BLUE_DARK, font=fonts["h1"])
    ry = y + 46
    if data.get("class_schedule"):
        for ln in _wrap(data["class_schedule"], fonts["small"], content_w - 140, draw):
            draw.text((pad + 22, ry), ln, fill=C_MUTED, font=fonts["small"])
            ry += _lh(fonts["small"])
        ry += 6
    for ln in layout["roadmap_lines"]:
        draw.text((pad + 22, ry), ln, fill=C_TEXT, font=fonts["body"])
        ry += _lh(fonts["body"])
    if ci:
        _paste_rgba(img, ci, (W - pad - 115, y + 10), (100, 90))
    y += rh + 12

    draw.text(
        (pad, H - 28),
        f"{brand} — Kiểm tra năng lực đầu vào {data['course']}",
        fill=C_MUTED,
        font=fonts["small"],
    )

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    img.save(output_path, "PNG", optimize=True)
    return output_path
