"""Challenge mặc định vòng 2–4 (seed vào scratch_challenges)."""

DEFAULT_CHALLENGES = [
    {
        "slug": "speed-square-order",
        "round": 2,
        "kind": "block_order",
        "title": "Sắp xếp vẽ hình vuông",
        "prompt": "Sắp xếp đúng thứ tự khối để vẽ hình vuông cạnh 100.",
        "points": 20,
        "time_limit_sec": 60,
        "blocks": [
            {"id": "a", "op": "pen_down", "label": "Đặt bút xuống"},
            {"id": "b", "op": "repeat", "label": "Lặp lại 4 lần", "times": 4},
            {"id": "c", "op": "move", "label": "Di chuyển 100 bước", "steps": 100},
            {"id": "d", "op": "turn_right", "label": "Xoay phải 90 độ", "degrees": 90},
        ],
        # Thứ tự đúng: pen_down → repeat( chứa move + turn ) — chấm dạng sequence phẳng bắt buộc
        "solution_order": ["a", "b", "c", "d"],
        "solution_note": "pen_down, rồi trong lặp 4: move 100 + turn 90",
    },
    {
        "slug": "speed-circle-expr",
        "round": 2,
        "kind": "block_order",
        "title": "Vẽ hình tròn",
        "prompt": "Sắp xếp: đặt bút → lặp 360 → di chuyển 2*3.14*100/360 → xoay phải 1°",
        "points": 20,
        "time_limit_sec": 60,
        "blocks": [
            {"id": "p", "op": "pen_down", "label": "Đặt bút xuống"},
            {"id": "r", "op": "repeat", "label": "Lặp lại 360 lần", "times": 360},
            {"id": "m", "op": "move", "label": "Di chuyển 2*3.14*100/360", "steps": "2*3.14*100/360"},
            {"id": "t", "op": "turn_right", "label": "Xoay phải 1 độ", "degrees": 1},
        ],
        "solution_order": ["p", "r", "m", "t"],
    },
    {
        "slug": "finish-collect-stars",
        "round": 3,
        "kind": "mission",
        "title": "Thu thập sao",
        "prompt": (
            "Nhân vật bắt đầu tại x=-100. Dùng lặp + di chuyển để đi tới x=100 và "
            "thu thập ít nhất 3 sao (mô phỏng). Hoàn thành khi đạt mục tiêu."
        ),
        "points": 25,
        "time_limit_sec": 90,
        "mission": {
            "start_x": -100,
            "goal_x": 100,
            "stars_needed": 3,
            "allowed_ops": ["repeat", "move", "change_x", "if_touching"],
        },
        "solution_checks": {"min_ops": 2, "must_include": ["repeat"]},
    },
    {
        "slug": "finish-bounce",
        "round": 3,
        "kind": "mission",
        "title": "Bật lại khi chạm cạnh",
        "prompt": "Xây chương trình: lặp mãi → di chuyển → nếu chạm cạnh thì bật lại (đổi hướng).",
        "points": 25,
        "time_limit_sec": 90,
        "mission": {
            "allowed_ops": ["forever", "move", "if_edge", "bounce"],
        },
        "solution_checks": {"must_include": ["forever", "move"], "any_of": ["bounce", "if_edge"]},
    },
    {
        "slug": "duel-broadcast",
        "round": 4,
        "kind": "mcq_hard",
        "title": "Phát tin và đợi",
        "prompt": "Khác biệt chính của «phát tin … và đợi» so với «phát tin» là gì?",
        "points": 30,
        "time_limit_sec": 45,
        "options": [
            {"id": "A", "text": "Chờ script nhận tin chạy xong rồi mới làm tiếp"},
            {"id": "B", "text": "Chỉ gửi được cho sân khấu"},
            {"id": "C", "text": "Tự động xóa biến"},
            {"id": "D", "text": "Không khác gì phát tin thường"},
        ],
        "correct_option_id": "A",
    },
    {
        "slug": "duel-direction",
        "round": 4,
        "kind": "mcq_hard",
        "title": "Hướng 0 độ trong Scratch",
        "prompt": "Trong Scratch, hướng 0 độ nghĩa là nhân vật nhìn về đâu?",
        "points": 30,
        "time_limit_sec": 40,
        "options": [
            {"id": "A", "text": "Lên trên"},
            {"id": "B", "text": "Sang phải"},
            {"id": "C", "text": "Xuống dưới"},
            {"id": "D", "text": "Sang trái"},
        ],
        "correct_option_id": "A",
    },
]

AI_PROFILES = {
    "easy": {"name": "Bot Mèo Con", "buzz_ms": (1800, 3200), "accuracy": 0.55, "color": "#60a5fa"},
    "medium": {"name": "Bot Cáo", "buzz_ms": (900, 1800), "accuracy": 0.72, "color": "#a78bfa"},
    "hard": {"name": "Bot Rồng", "buzz_ms": (450, 1100), "accuracy": 0.88, "color": "#f472b6"},
}
