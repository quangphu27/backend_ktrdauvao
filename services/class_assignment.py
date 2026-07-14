"""Xếp lớp học — Python 1 lớp, Scratch theo danh sách phân lớp."""

import re
import unicodedata

PYTHON_CLASS = {
    "name": "Lớp Python",
    "schedule": "",
}

SCRATCH_CLASSES = {
    1: {
        "name": "Lớp Scratch 1",
        "schedule": "Tối các ngày Thứ 3 (6h30–8h), Thứ 7 (6h30–8h)",
    },
    2: {
        "name": "Lớp Scratch 2",
        "schedule": "Tối Thứ 4 (6h30–8h), Sáng Chủ nhật (8h30–10h)",
    },
    3: {
        "name": "Lớp Scratch 3",
        "schedule": "Tối các ngày Thứ 6 (6h30–8h), Chủ nhật (6h30–8h)",
    },
}

SCRATCH_CLASS_ROADMAP = {
    1: [
        "Ôn luyện và củng cố kiến thức về các khối lệnh",
        "Thực hành nhiều bài tập để nhớ rõ và phát triển tư duy",
        "Sáng tạo và phát triển khả năng lập trình",
    ],
    2: [
        "Học chắc kiến thức về các khối lệnh kết hợp các bài tập",
        "Xây dựng các chương trình và trò chơi để ghi nhớ kiến thức và phát triển tư duy",
    ],
    3: [
        "Dành thời gian để trẻ làm quen với máy tính và lập trình",
        "Học chắc kiến thức nền tảng",
        "Kết hợp làm bài tập và xây dựng các chương trình",
    ],
}

# Tên hiển thị chuẩn tiếng Việt: (SĐT 9 số, tên chuẩn hóa) -> tên đầy đủ
_DISPLAY_NAMES = {
    ("969913468", "tran quang tuan kiet"): "Trần Quang Tuấn Kiệt",
    ("946930682", "dao nguyen khoi"): "Đào Nguyễn Khôi",
    ("386652361", "truong minh dung"): "Trương Minh Dung",
    ("394952882", "nguyen ha trieu man"): "Nguyễn Hà Triệu Mẫn",
    ("92365128", "le cong quoc an"): "Lê Công Quốc An",
    ("792341192", "duong duc hieu"): "Dương Đức Hiếu",
    ("988117820", "nguyen minh an"): "Nguyễn Minh An",
    ("888287288", "nguyen dai quang"): "Nguyễn Đại Quang",
    ("355587508", "nguyen ngoc thao nguyen"): "Nguyễn Ngọc Thảo Nguyên",
    ("982330325", "nguyen quynh an"): "Nguyễn Quỳnh An",
    ("394952882", "nguyen ha trieu minh"): "Nguyễn Hà Triệu Minh",
    ("941820920", "nguyen thi huyen trang"): "Nguyễn Thị Huyền Trang",
    ("977201518", "nguyen huu tai"): "Nguyễn Hữu Tài",
    ("914952786", "tran ngoc phuong anh"): "Trần Ngọc Phương Anh",
    ("399399779", "nguyen vu thien an"): "Nguyễn Vũ Thiên Ân",
    ("989231287", "tran le hai binh"): "Trần Lê Hải Bình",
    ("975195243", "nguyen linh chi"): "Nguyễn Linh Chi",
    ("946930682", "dao vu dang khoi"): "Đào Vũ Đăng Khôi",
    ("974097939", "viet anh"): "Việt Anh",
    ("902911606", "duong phuc khang"): "Dương Phúc Khang",
    ("989231287", "thien phu"): "Thiên Phú",
    ("903136861", "hoang khang"): "Hoàng Khang",
    ("972027087", "nguyen ha minh kiet"): "Nguyễn Hà Minh Kiệt",
    ("966773737", "nguyen dinh hoang vuong"): "Nguyễn Đình Hoàng Vương",
    ("909510029", "tran gia khang"): "Trần Gia Khang",
    ("989948041", "hoang bao"): "Hoàng Bảo",
}

# (số điện thoại chuẩn hóa 9 số, tên chuẩn hóa, mã lớp)
_SCRATCH_ROSTER = [
    ("969913468", "tran quang tuan kiet", 1),
    ("946930682", "dao nguyen khoi", 1),
    ("386652361", "truong minh dung", 1),
    ("394952882", "nguyen ha trieu man", 1),
    ("92365128", "le cong quoc an", 1),
    ("792341192", "duong duc hieu", 1),
    ("988117820", "nguyen minh an", 1),
    ("888287288", "nguyen dai quang", 1),
    ("355587508", "nguyen ngoc thao nguyen", 1),
    ("982330325", "nguyen quynh an", 2),
    ("394952882", "nguyen ha trieu minh", 2),
    ("941820920", "nguyen thi huyen trang", 2),
    ("977201518", "nguyen huu tai", 2),
    ("914952786", "tran ngoc phuong anh", 2),
    ("399399779", "nguyen vu thien an", 2),
    ("989231287", "tran le hai binh", 2),
    ("975195243", "nguyen linh chi", 2),
    ("946930682", "dao vu dang khoi", 2),
    ("974097939", "viet anh", 3),
    ("902911606", "duong phuc khang", 3),
    ("989231287", "thien phu", 3),
    ("903136861", "hoang khang", 3),
    ("972027087", "nguyen ha minh kiet", 3),
    ("966773737", "nguyen dinh hoang vuong", 3),
    ("909510029", "tran gia khang", 3),
    ("989948041", "hoang bao", 3),
]

_ROSTER_BY_KEY = {(p, n): cid for p, n, cid in _SCRATCH_ROSTER}
_PHONES = {}
for phone, name, cid in _SCRATCH_ROSTER:
    _PHONES.setdefault(phone, []).append((name, cid))


def normalize_phone(phone):
    digits = re.sub(r"\D", "", str(phone or ""))
    if digits.startswith("84") and len(digits) >= 11:
        digits = digits[2:]
    if digits.startswith("0") and len(digits) > 9:
        digits = digits[1:]
    return digits


def normalize_name(name):
    if not name:
        return ""
    s = unicodedata.normalize("NFKD", str(name).strip())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("đ", "d").replace("Đ", "d").lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _score_fallback_class(score):
    if score >= 80:
        return 1
    if score >= 60:
        return 2
    return 3


def find_scratch_class(phone=None, student_name=None, score=0):
    p = normalize_phone(phone)
    n = normalize_name(student_name)
    if p and n and (p, n) in _ROSTER_BY_KEY:
        cid = _ROSTER_BY_KEY[(p, n)]
        return {**SCRATCH_CLASSES[cid], "class_id": cid}

    if p and p in _PHONES:
        matches = _PHONES[p]
        if len(matches) == 1:
            cid = matches[0][1]
            return {**SCRATCH_CLASSES[cid], "class_id": cid}
        if n:
            for name, cid in matches:
                if name == n or name in n or n in name:
                    return {**SCRATCH_CLASSES[cid], "class_id": cid}

    if not p and n:
        for (rp, rn), cid in _ROSTER_BY_KEY.items():
            if rn == n or rn in n or n in rn:
                return {**SCRATCH_CLASSES[cid], "class_id": cid}

    cid = _score_fallback_class(float(score or 0))
    return {**SCRATCH_CLASSES[cid], "class_id": cid}


def get_recommendation(course_slug, score, phone=None, student_name=None):
    slug = (course_slug or "").lower()
    if slug == "scratch":
        return find_scratch_class(phone, student_name, score)["name"]
    return PYTHON_CLASS["name"]


def format_display_name(raw_name, phone=None):
    """Chuẩn hóa tên học sinh sang tiếng Việt có dấu."""
    p = normalize_phone(phone)
    n = normalize_name(raw_name)
    if p and n and (p, n) in _DISPLAY_NAMES:
        return _DISPLAY_NAMES[(p, n)]
    if n:
        for (rp, rn), display in _DISPLAY_NAMES.items():
            if rn == n or (not p and (rn in n or n in rn)):
                return display
    return _title_vietnamese_name(raw_name)


def _title_vietnamese_name(name):
    if not name or not str(name).strip():
        return "Học sinh"
    parts = str(name).strip().split()
    out = []
    for w in parts:
        if len(w) <= 1:
            out.append(w.upper())
        else:
            out.append(w[0].upper() + w[1:].lower())
    return " ".join(out)


def get_scratch_class_roadmap(class_id):
    return list(SCRATCH_CLASS_ROADMAP.get(class_id, SCRATCH_CLASS_ROADMAP[3]))


def get_class_info(course_slug, phone=None, student_name=None, score=0):
    slug = (course_slug or "").lower()
    if slug == "scratch":
        return find_scratch_class(phone, student_name, score)
    return dict(PYTHON_CLASS)


def filter_study_roadmap(bullets, class_name="", schedule=""):
    """Bỏ tên lớp / lịch học khỏi gạch đầu dòng — hiển thị riêng phía trên."""
    out = []
    for item in bullets or []:
        t = (item or "").strip()
        if not t:
            continue
        if class_name and t == class_name:
            continue
        if schedule and (t == schedule or t == f"Lịch học: {schedule}"):
            continue
        if t.startswith("Lịch học:"):
            continue
        if class_name and t.startswith(class_name):
            continue
        out.append(t)
    return out
