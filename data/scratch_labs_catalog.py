"""5 bài Scratch lab — đề + đáp án mẫu (cây khối)."""

LABS = [
    {
        "slug": "ve-hinh-tron",
        "title": "Vẽ hình tròn",
        "order": 1,
        "points": 2,
        "prompt": (
            "Vẽ hình tròn bán kính 100:\n"
            "• Đặt bút xuống\n"
            "• Lặp lại 360 lần: di chuyển (2 × 3.14 × 100 / 360) bước, xoay phải 1 độ\n"
            "Gợi ý: có thể viết biểu thức 2*3.14*100/360 trong ô di chuyển."
        ),
        "hints": [
            "Nhớ khối Đặt bút xuống trước khi di chuyển",
            "Lặp 360 lần, mỗi lần xoay đúng 1 độ",
            "Quãng mỗi bước = chu vi / 360 = 2*3.14*100/360",
        ],
        "palette": ["when_flag", "pen_clear", "pen_down", "repeat", "move", "turn_right", "goto_xy"],
        "starter": {
            "version": 1,
            "sprites": [
                {
                    "name": "Mèo",
                    "scripts": [{"hat": "when_flag", "body": []}],
                }
            ],
        },
        "solution": {
            "version": 1,
            "sprites": [
                {
                    "name": "Mèo",
                    "scripts": [
                        {
                            "hat": "when_flag",
                            "body": [
                                {"op": "pen_down"},
                                {
                                    "op": "repeat",
                                    "times": "360",
                                    "body": [
                                        {"op": "move", "steps": "2*3.14*100/360"},
                                        {"op": "turn_right", "degrees": "1"},
                                    ],
                                },
                            ],
                        }
                    ],
                }
            ],
        },
    },
    {
        "slug": "ve-hinh-vuong",
        "title": "Vẽ hình vuông",
        "order": 2,
        "points": 2,
        "prompt": (
            "Vẽ hình vuông cạnh 100 bước:\n"
            "• Đặt bút xuống\n"
            "• Lặp 4 lần: di chuyển 100 bước, xoay phải 90 độ"
        ),
        "hints": [
            "Hình vuông có 4 cạnh → lặp 4 lần",
            "Góc ngoài mỗi đỉnh = 90 độ",
        ],
        "palette": ["when_flag", "pen_clear", "pen_down", "repeat", "move", "turn_right", "goto_xy"],
        "starter": {
            "version": 1,
            "sprites": [{"name": "Mèo", "scripts": [{"hat": "when_flag", "body": []}]}],
        },
        "solution": {
            "version": 1,
            "sprites": [
                {
                    "name": "Mèo",
                    "scripts": [
                        {
                            "hat": "when_flag",
                            "body": [
                                {"op": "pen_down"},
                                {
                                    "op": "repeat",
                                    "times": "4",
                                    "body": [
                                        {"op": "move", "steps": "100"},
                                        {"op": "turn_right", "degrees": "90"},
                                    ],
                                },
                            ],
                        }
                    ],
                }
            ],
        },
    },
    {
        "slug": "meo-bat-chuot",
        "title": "Mèo bắt chuột",
        "order": 3,
        "points": 3,
        "prompt": (
            "Hai nhân vật:\n"
            "• Chuột: lặp lại mãi → đi tới con trỏ chuột\n"
            "• Mèo: lặp lại mãi → hướng về con trỏ chuột, di chuyển 3 bước\n"
            "(Dùng đúng các khối trong bảng chọn.)"
        ),
        "hints": [
            "Chuột bám theo con trỏ",
            "Mèo vừa quay hướng vừa tiến lại gần",
        ],
        "palette": [
            "when_flag",
            "forever",
            "goto_mouse",
            "point_mouse",
            "move",
        ],
        "multi_sprite": True,
        "starter": {
            "version": 1,
            "sprites": [
                {"name": "Chuột", "role": "mouse", "scripts": [{"hat": "when_flag", "body": []}]},
                {"name": "Mèo", "role": "cat", "scripts": [{"hat": "when_flag", "body": []}]},
            ],
        },
        "solution": {
            "version": 1,
            "sprites": [
                {
                    "name": "Chuột",
                    "scripts": [
                        {
                            "hat": "when_flag",
                            "body": [
                                {
                                    "op": "forever",
                                    "body": [{"op": "goto_mouse"}],
                                }
                            ],
                        }
                    ],
                },
                {
                    "name": "Mèo",
                    "scripts": [
                        {
                            "hat": "when_flag",
                            "body": [
                                {
                                    "op": "forever",
                                    "body": [
                                        {"op": "point_mouse"},
                                        {"op": "move", "steps": "3"},
                                    ],
                                }
                            ],
                        }
                    ],
                },
            ],
        },
    },
    {
        "slug": "to-mau-hinh-tron",
        "title": "Tô màu hình tròn",
        "order": 4,
        "points": 2,
        "prompt": (
            "Tô màu hình tròn bán kính ~100:\n"
            "• Đặt màu bút (ví dụ đỏ)\n"
            "• Đặt cỡ bút 20\n"
            "• Đặt bút xuống\n"
            "• Lặp 360 lần: di chuyển 2*3.14*100/360 bước, xoay phải 1 độ"
        ),
        "hints": [
            "Đặt màu và cỡ bút trước khi vẽ",
            "Cỡ bút lớn giúp nét tròn trông như được tô",
        ],
        "palette": [
            "when_flag",
            "pen_clear",
            "pen_color",
            "pen_size",
            "pen_down",
            "repeat",
            "move",
            "turn_right",
        ],
        "starter": {
            "version": 1,
            "sprites": [{"name": "Mèo", "scripts": [{"hat": "when_flag", "body": []}]}],
        },
        "solution": {
            "version": 1,
            "sprites": [
                {
                    "name": "Mèo",
                    "scripts": [
                        {
                            "hat": "when_flag",
                            "body": [
                                {"op": "pen_color", "color": "red"},
                                {"op": "pen_size", "size": "20"},
                                {"op": "pen_down"},
                                {
                                    "op": "repeat",
                                    "times": "360",
                                    "body": [
                                        {"op": "move", "steps": "2*3.14*100/360"},
                                        {"op": "turn_right", "degrees": "1"},
                                    ],
                                },
                            ],
                        }
                    ],
                }
            ],
        },
    },
    {
        "slug": "dan-piano",
        "title": "Đàn piano",
        "order": 5,
        "points": 3,
        "prompt": (
            "Tạo đàn piano 5 phím:\n"
            "• Khi nhấn phím 1 → phát nốt C\n"
            "• Khi nhấn phím 2 → phát nốt D\n"
            "• Khi nhấn phím 3 → phát nốt E\n"
            "• Khi nhấn phím 4 → phát nốt F\n"
            "• Khi nhấn phím 5 → phát nốt G"
        ),
        "hints": [
            "Mỗi phím = một script «Khi nhấn phím …»",
            "Dùng khối Phát nốt với tên C, D, E, F, G",
        ],
        "palette": ["when_key", "play_note"],
        "starter": {
            "version": 1,
            "sprites": [
                {
                    "name": "Piano",
                    "scripts": [
                        {"hat": "when_key", "key": "1", "body": []},
                        {"hat": "when_key", "key": "2", "body": []},
                        {"hat": "when_key", "key": "3", "body": []},
                        {"hat": "when_key", "key": "4", "body": []},
                        {"hat": "when_key", "key": "5", "body": []},
                    ],
                }
            ],
        },
        "solution": {
            "version": 1,
            "sprites": [
                {
                    "name": "Piano",
                    "scripts": [
                        {"hat": "when_key", "key": "1", "body": [{"op": "play_note", "sound": "c"}]},
                        {"hat": "when_key", "key": "2", "body": [{"op": "play_note", "sound": "d"}]},
                        {"hat": "when_key", "key": "3", "body": [{"op": "play_note", "sound": "e"}]},
                        {"hat": "when_key", "key": "4", "body": [{"op": "play_note", "sound": "f"}]},
                        {"hat": "when_key", "key": "5", "body": [{"op": "play_note", "sound": "g"}]},
                    ],
                }
            ],
        },
    },
]


def get_lab(slug: str):
    for lab in LABS:
        if lab["slug"] == slug:
            return lab
    return None


def public_lab(lab: dict) -> dict:
    """Ẩn solution khỏi client."""
    return {
        "slug": lab["slug"],
        "title": lab["title"],
        "order": lab["order"],
        "points": lab["points"],
        "prompt": lab["prompt"],
        "hints": lab.get("hints") or [],
        "palette": lab.get("palette") or [],
        "multi_sprite": bool(lab.get("multi_sprite")),
        "starter": lab.get("starter") or {},
    }
