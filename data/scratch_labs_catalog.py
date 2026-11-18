"""5 bài Scratch lab — đề + đáp án mẫu (cây khối).

Starter = khối đã ghi sẵn (xáo thứ tự, ô số để trống) để học sinh sắp xếp + điền số.
"""


def _blk(op, **fields):
    """Khối starter (client sẽ gán id)."""
    item = {"op": op}
    item.update(fields)
    if op in ("repeat", "forever") and "body" not in item:
        item["body"] = []
    return item


LABS = [
    {
        "slug": "ve-hinh-tron",
        "title": "Vẽ hình tròn",
        "order": 1,
        "points": 2,
        "prompt": (
            "Vẽ hình tròn bán kính 100 trên sân khấu.\n"
            "Sắp xếp các khối đã cho và điền số / biểu thức cho đúng."
        ),
        "hints": [
            "Nhớ đặt bút xuống trước khi vẽ",
            "Chu vi hình tròn = 2 × 3.14 × bán kính",
        ],
        "palette": ["when_flag", "pen_clear", "pen_down", "repeat", "move", "turn_right", "goto_xy"],
        "starter": {
            "version": 1,
            "sprites": [
                {
                    "name": "Mèo",
                    "scripts": [
                        {
                            "hat": "when_flag",
                            "body": [
                                _blk("move", steps=""),
                                _blk("repeat", times="", body=[]),
                                _blk("pen_down"),
                                _blk("turn_right", degrees=""),
                            ],
                        }
                    ],
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
            "Vẽ hình vuông cạnh 100 bước.\n"
            "Sắp xếp các khối đã cho và điền số cho đúng."
        ),
        "hints": [
            "Hình vuông có 4 cạnh",
            "Góc ngoài mỗi đỉnh bằng nhau",
        ],
        "palette": ["when_flag", "pen_clear", "pen_down", "repeat", "move", "turn_right", "goto_xy"],
        "starter": {
            "version": 1,
            "sprites": [
                {
                    "name": "Mèo",
                    "scripts": [
                        {
                            "hat": "when_flag",
                            "body": [
                                _blk("turn_right", degrees=""),
                                _blk("pen_down"),
                                _blk("move", steps=""),
                                _blk("repeat", times="", body=[]),
                            ],
                        }
                    ],
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
            "Hai nhân vật Chuột và Mèo: chuột bám theo con trỏ; "
            "mèo đuổi theo (hướng về con trỏ rồi tiến lại).\n"
            "Sắp xếp khối đã cho cho từng nhân vật."
        ),
        "hints": [
            "Mỗi nhân vật có script riêng",
            "Dùng «lặp lại mãi» để chạy liên tục",
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
                {
                    "name": "Chuột",
                    "role": "mouse",
                    "scripts": [
                        {
                            "hat": "when_flag",
                            "body": [
                                _blk("goto_mouse"),
                                _blk("forever", body=[]),
                            ],
                        }
                    ],
                },
                {
                    "name": "Mèo",
                    "role": "cat",
                    "scripts": [
                        {
                            "hat": "when_flag",
                            "body": [
                                _blk("move", steps=""),
                                _blk("forever", body=[]),
                                _blk("point_mouse"),
                            ],
                        }
                    ],
                },
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
            "Tô màu một hình tròn (bán kính khoảng 100) bằng bút dày màu đỏ.\n"
            "Sắp xếp các khối đã cho và điền số / biểu thức cho đúng."
        ),
        "hints": [
            "Đặt màu và cỡ bút trước khi vẽ",
            "Cỡ bút lớn giúp nét trông như được tô",
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
            "sprites": [
                {
                    "name": "Mèo",
                    "scripts": [
                        {
                            "hat": "when_flag",
                            "body": [
                                _blk("move", steps=""),
                                _blk("pen_size", size=""),
                                _blk("repeat", times="", body=[]),
                                _blk("pen_color", color=""),
                                _blk("turn_right", degrees=""),
                                _blk("pen_down"),
                            ],
                        }
                    ],
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
            "Tạo đàn piano 5 phím (1–5).\n"
            "Với mỗi phím: sắp xếp / điền nốt sao cho đúng thứ tự âm thanh."
        ),
        "hints": [
            "Mỗi phím một script «Khi nhấn phím …»",
            "Nốt lần lượt theo thang C D E F G",
        ],
        "palette": ["when_key", "play_note"],
        "starter": {
            "version": 1,
            "sprites": [
                {
                    "name": "Piano",
                    "scripts": [
                        {"hat": "when_key", "key": "1", "body": [_blk("play_note", sound="")]},
                        {"hat": "when_key", "key": "2", "body": [_blk("play_note", sound="")]},
                        {"hat": "when_key", "key": "3", "body": [_blk("play_note", sound="")]},
                        {"hat": "when_key", "key": "4", "body": [_blk("play_note", sound="")]},
                        {"hat": "when_key", "key": "5", "body": [_blk("play_note", sound="")]},
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
