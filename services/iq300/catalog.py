"""8 thử thách IQ 300 — đáp án chỉ dùng phía server."""

# Điểm theo đề: 10+10+15+15+20+20+25+35 = 150
CHALLENGES = [
    {
        "id": 1,
        "slug": "mystery-sequence",
        "title": "Quy luật bí ẩn",
        "difficulty": "Dễ",
        "points": 10,
        "kind": "mcq",
        "prompt": "Tìm số tiếp theo trong dãy: 2 – 6 – 12 – 20 – 30 – ?",
        "options": [
            {"id": "A", "text": "36"},
            {"id": "B", "text": "40"},
            {"id": "C", "text": "42"},
            {"id": "D", "text": "44"},
        ],
        "correct": "C",
        "explanation": "Hiệu lần lượt: +4, +6, +8, +10 → tiếp theo +12; 30+12=42.",
    },
    {
        "id": 2,
        "slug": "odd-shape-out",
        "title": "Tìm kẻ khác biệt",
        "difficulty": "Dễ–TB",
        "points": 10,
        "kind": "shape_pick",
        "prompt": "Hình nào khác biệt nhất nếu xét số cạnh?",
        "shapes": [
            {"id": "square", "label": "Hình vuông", "sides": 4},
            {"id": "triangle", "label": "Hình tam giác", "sides": 3},
            {"id": "pentagon", "label": "Hình ngũ giác", "sides": 5},
            {"id": "circle", "label": "Hình tròn", "sides": 0},
        ],
        "correct": "circle",
        "explanation": "Vuông/tam giác/ngũ giác có cạnh; hình tròn không có cạnh (hoặc vô hạn cung).",
    },
    {
        "id": 3,
        "slug": "number-cipher",
        "title": "Mật mã số học",
        "difficulty": "Trung bình",
        "points": 15,
        "kind": "mcq",
        "prompt": "3+3=18 · 4+4=32 · 5+5=50 · 6+6=?",
        "options": [
            {"id": "A", "text": "60"},
            {"id": "B", "text": "66"},
            {"id": "C", "text": "72"},
            {"id": "D", "text": "36"},
        ],
        "correct": "C",
        "explanation": "a+a theo quy luật a×a×2: 6×6×2=72.",
    },
    {
        "id": 4,
        "slug": "mislabeled-boxes",
        "title": "Câu đố cân não",
        "difficulty": "Trung bình",
        "points": 15,
        "kind": "box_pick",
        "prompt": (
            "3 hộp nhãn: A «Táo», B «Cam», C «Táo và Cam». Cả 3 nhãn đều SAI. "
            "Chỉ được lấy một quả từ một hộp. Lấy từ hộp nào để suy ra cả 3?"
        ),
        "boxes": [
            {"id": "A", "label": "Táo"},
            {"id": "B", "label": "Cam"},
            {"id": "C", "label": "Táo và Cam"},
        ],
        "correct": "C",
        "explanation": (
            "Nhãn C sai → C chỉ chứa một loại. Lấy 1 quả từ C biết loại đó; "
            "hai hộp còn lại suy ra vì mọi nhãn đều sai."
        ),
    },
    {
        "id": 5,
        "slug": "painted-cube",
        "title": "Tư duy không gian",
        "difficulty": "TB–Khó",
        "points": 20,
        "kind": "mcq",
        "prompt": (
            "Khối 3×3×3 (27 khối nhỏ) sơn toàn bộ mặt ngoài. "
            "Có bao nhiêu khối nhỏ được sơn đúng 2 mặt?"
        ),
        "options": [
            {"id": "A", "text": "6"},
            {"id": "B", "text": "8"},
            {"id": "C", "text": "12"},
            {"id": "D", "text": "24"},
        ],
        "correct": "C",
        "explanation": "Mỗi cạnh có 1 khối giữa (không góc); 12 cạnh → 12 khối sơn đúng 2 mặt.",
    },
    {
        # Đề gốc ghi đáp án An nhưng logic chỉ thỏa khi Bình nói thật → dùng Bình.
        "id": 6,
        "slug": "who-tells-truth",
        "title": "Ai đang nói dối?",
        "difficulty": "Khó",
        "points": 20,
        "kind": "mcq",
        "prompt": (
            "An, Bình, Chi — đúng một người nói thật, hai người nói dối.\n"
            "An: «Bình nói dối.»\n"
            "Bình: «Chi nói dối.»\n"
            "Chi: «An và Bình đều nói dối.»\n"
            "Ai nói thật?"
        ),
        "options": [
            {"id": "A", "text": "An"},
            {"id": "B", "text": "Bình"},
            {"id": "C", "text": "Chi"},
            {"id": "D", "text": "Không xác định được"},
        ],
        "correct": "B",
        "explanation": (
            "Nếu Bình nói thật: Chi nói dối; An nói dối (vì «Bình nói dối» sai). "
            "Chi nói dối nên phủ định «An và Bình đều nói dối» — khớp vì Bình thật. "
            "Các trường hợp An/Chi thật đều mâu thuẫn."
        ),
    },
    {
        "id": 7,
        "slug": "symbol-pattern",
        "title": "Phản xạ và quy luật",
        "difficulty": "Khó",
        "points": 25,
        "kind": "symbol_pick",
        "prompt": "Chuỗi: ▲ ● ▲ ▲ ● ▲ ▲ ▲ ● ? — ký hiệu tiếp theo là gì?",
        "sequence": ["tri", "dot", "tri", "tri", "dot", "tri", "tri", "tri", "dot"],
        "options": [
            {"id": "tri", "label": "▲"},
            {"id": "dot", "label": "●"},
            {"id": "sq", "label": "■"},
            {"id": "dia", "label": "◆"},
        ],
        "correct": "tri",
        "explanation": "Nhóm ▲ tăng dần (1,2,3…) xen ●; sau ● của nhóm 3 bắt đầu nhóm 4 bằng ▲.",
        "observe_sec": 8,
    },
    {
        "id": 8,
        "slug": "balance-coins",
        "title": "Thử thách trùm cuối",
        "difficulty": "Rất khó",
        "points": 35,
        "kind": "balance",
        "prompt": (
            "9 đồng xu giống nhau, một đồng nhẹ hơn. Cân thăng bằng, tối đa 2 lần cân. "
            "Tìm đồng nhẹ."
        ),
        "coin_count": 9,
        "max_weighings": 2,
        # Server sinh light_coin_index khi tạo attempt (0..8)
        "explanation": (
            "Chia 3 nhóm × 3. Cân nhóm1 vs nhóm2 → nhóm nhẹ (hoặc nhóm3 nếu cân bằng). "
            "Cân 2 đồng trong nhóm nghi vấn → đồng nhẹ hoặc đồng còn lại."
        ),
    },
]


def public_challenges():
    """Ẩn đáp án / explanation khi gửi client lúc chơi."""
    out = []
    for ch in CHALLENGES:
        item = {
            "id": ch["id"],
            "slug": ch["slug"],
            "title": ch["title"],
            "difficulty": ch["difficulty"],
            "points": ch["points"],
            "kind": ch["kind"],
            "prompt": ch["prompt"],
        }
        for key in ("options", "shapes", "boxes", "sequence", "observe_sec", "coin_count", "max_weighings"):
            if key in ch:
                item[key] = ch[key]
        out.append(item)
    return out


def get_challenge(cid: int):
    for ch in CHALLENGES:
        if ch["id"] == int(cid):
            return ch
    return None


def rank_title(score: int) -> str:
    s = int(score or 0)
    if s >= 140:
        return "Siêu trí tuệ"
    if s >= 120:
        return "Cao thủ logic"
    if s >= 90:
        return "Bậc thầy tư duy"
    if s >= 50:
        return "Người quan sát tinh anh"
    return "Nhà thám hiểm mới"
