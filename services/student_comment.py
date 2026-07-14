"""Sinh nhận xét theo mẫu — cá nhân hóa, đa dạng từ ngữ."""

CATEGORY_VI = {
    "logic": "tư duy logic",
    "observation": "quan sát",
    "problem_solving": "giải quyết vấn đề",
    "sequencing": "sắp xếp khối lệnh",
    "memory": "đọc hiểu code",
    "math": "tính toán",
    "algorithm": "thuật toán",
}

SCRATCH_CATEGORY_VI = {
    **CATEGORY_VI,
    "memory": "phân tích khối lệnh",
    "sequencing": "sắp xếp thứ tự khối",
}

# Mỗi chủ đề nhiều cách diễn đạt (chọn theo seed học sinh)
FOUNDATION_HINT = {
    "scratch": {
        "sequencing": [
            "Luyện ghép khối Sự kiện, Chuyển động theo đúng thứ tự chạy.",
            "Tập sắp xếp khối lệnh từ cờ xanh ▶️ đến các lệnh di chuyển.",
            "Thực hành xếp khối theo trình tự để nhân vật chạy đúng ý.",
            "Ôn cách nối khối Sự kiện với khối Chuyển động một cách logic.",
        ],
        "algorithm": [
            "Ôn khối Lặp lại và Nếu — thì qua các bài tình huống đơn giản.",
            "Luyện dùng vòng lặp và điều kiện để điều khiển nhân vật.",
            "Tập tư duy theo bước khi gặp khối lặp và khối kiểm tra điều kiện.",
            "Thử ghép vòng lặp với di chuyển để thấy rõ chương trình chạy.",
        ],
        "observation": [
            "Quan sát kỹ hình minh họa trước khi chọn đáp án.",
            "Chú ý chi tiết trong ảnh và mô tả tình huống của đề.",
            "Rèn mắt nhìn hình, đọc kỹ tình huống rồi mới suy luận.",
            "Luyện bài quan sát — xem hình và đoán kết quả chương trình.",
        ],
        "logic": [
            "Rèn suy luận qua các bài chọn khối lệnh phù hợp.",
            "Tập phân tích đề bài rồi mới quyết định khối nào đúng.",
            "Luyện tư duy logic bằng cách giải thích vì sao chọn đáp án đó.",
            "Thử tự đặt câu hỏi «nếu… thì…» khi đọc đề Scratch.",
            "Chơi thử các bài đố vui khối lệnh để rèn tư duy.",
        ],
        "math": [
            "Luyện tính nhẩm: số lần lặp × số bước di chuyển.",
            "Ôn phép nhân, cộng khi đọc các bài có vòng lặp.",
            "Tập ước lượng kết quả trước khi chạy thử chương trình.",
        ],
        "memory": [
            "Đọc từng khối lệnh và hình dung chương trình chạy ra sao.",
            "Tập trace thứ tự khối bằng cách chỉ tay theo từng bước.",
            "Xem lại chương trình mẫu và tự giải thích từng khối.",
            "Luyện đọc hiểu chương trình Scratch có 4–5 khối trở lên.",
        ],
        "problem_solving": [
            "Thực hành các tình huống game đơn giản trên Scratch.",
            "Giải từng bài toán nhỏ bằng cách chia nhỏ yêu cầu đề bài.",
            "Luyện cách tìm lỗi khi nhân vật không chạy như mong muốn.",
        ],
    },
    "python": {
        "memory": [
            "Bắt đầu từ biến, print, if/else — đọc hiểu từng dòng.",
            "Luyện đọc code ngắn và dự đoán kết quả in ra màn hình.",
            "Tập trace từng dòng Python bằng giấy bút trước khi chạy.",
            "Ôn print, input và cách máy tính chạy lệnh tuần tự.",
        ],
        "algorithm": [
            "Ôn vòng lặp for/while và hàm range() qua ví dụ nhỏ.",
            "Luyện đếm từng vòng lặp để hiểu code chạy thế nào.",
            "Tập viết vòng lặp in dãy số đơn giản.",
            "Thử sửa code lặp và quan sát kết quả thay đổi ra sao.",
        ],
        "math": [
            "Luyện biểu thức, phép toán và toán tử % trong Python.",
            "Tập tính nhẩm kết quả trước khi chạy đoạn code.",
            "Ôn phép chia dư (%) qua các bài tập ngắn.",
        ],
        "logic": [
            "Rèn suy luận qua bài đọc hiểu kết quả in ra.",
            "Tập giải thích bằng lời vì sao đáp án A đúng, B sai.",
            "Luyện các câu đố vui về thứ tự chạy code.",
        ],
        "observation": [
            "Đọc kỹ từng chi tiết trong đề trước khi chọn.",
            "Gạch chân từ khóa trong câu hỏi để không bỏ sót ý.",
        ],
        "problem_solving": [
            "Giải bài tập nhỏ từng bước, không vội chọn đáp án.",
            "Chia nhỏ bài toán thành 2–3 bước rồi mới code.",
            "Luyện kiểm tra lại đáp án bằng cách chạy thử trong đầu.",
        ],
        "sequencing": [
            "Hiểu code chạy từ trên xuống, từng dòng một.",
            "Tập vẽ sơ đồ thứ tự thực thi cho đoạn code ngắn.",
        ],
    },
}

GROWTH_HINT = {
    "scratch": {
        "algorithm": [
            "Mở rộng thêm vòng lặp và điều kiện trong các bài khó hơn.",
            "Thử ghép lặp + điều kiện vào một mini-game nhỏ.",
            "Học cách dùng khối lặp để nhân vật làm việc lặp lại thông minh hơn.",
        ],
        "sequencing": [
            "Luyện sắp xếp khối phức tạp hơn và làm project nhỏ.",
            "Thử tự thiết kế trình tự khối cho một câu chuyện ngắn.",
        ],
        "logic": [
            "Thử thách bản thân với bài tư duy và giải quyết vấn đề mới.",
            "Tự đặt câu hỏi kiểm tra logic khi xem đáp án bạn bè.",
        ],
        "observation": [
            "Làm thêm bài quan sát hình ảnh, tình huống thực tế.",
            "Luyện mắt quan sát chi tiết trong tranh minh họa đề bài.",
        ],
        "math": [
            "Kết hợp tính toán với lập trình trong game Scratch.",
            "Tập tính toán trước khi chạy chương trình có vòng lặp.",
        ],
        "memory": [
            "Đọc phân tích chương trình Scratch nhiều khối hơn.",
            "Tự vẽ lại khối lệnh từ một chương trình mẫu.",
        ],
        "problem_solving": [
            "Làm animation hoặc game nhỏ để vận dụng kiến thức.",
            "Thử sửa lỗi trong chương trình bạn vừa ghép.",
        ],
    },
    "python": {
        "algorithm": [
            "Học thêm thuật toán cơ bản để tăng tư duy lập trình.",
            "Luyện bài toán đếm, tìm max/min bằng vòng lặp.",
            "Thử viết chương trình giải bài tập toán nhỏ.",
        ],
        "memory": [
            "Đọc code dài hơn và tự giải thích từng dòng.",
            "Luyện dự đoán output trước khi chạy chương trình.",
        ],
        "math": [
            "Ôn biểu thức và phép toán trong bài Python.",
            "Luyện tính nhẩm kết quả biểu thức trong code.",
        ],
        "logic": [
            "Luyện suy luận qua nhiều dạng câu đọc hiểu kết quả.",
            "Tập giải thích đáp án cho người khác nghe.",
        ],
        "observation": [
            "Rèn thói quen đọc kỹ đề, kiểm tra lại trước khi nộp.",
            "Chú ý từng chi tiết nhỏ trong câu hỏi trắc nghiệm.",
        ],
        "problem_solving": [
            "Làm bài tập kết hợp if/else và vòng lặp.",
            "Thử giải bài toán thực tế bằng code Python ngắn.",
        ],
        "sequencing": [
            "Hiểu sâu hơn về nhánh if/elif/else và thứ tự chạy.",
            "Vẽ sơ đồ luồng cho đoạn code có nhiều nhánh.",
        ],
    },
}

ROADMAP_OPEN = {
    "scratch": {
        "high_none": [
            "Tiếp tục học Scratch với các chủ đề mới,",
            "Duy trì thói quen luyện Scratch 2–3 buổi mỗi tuần,",
            "Khám phá thêm khối lệnh và tình huống thú vị trên Scratch,",
            "Nên thử sức với bài Scratch khó hơn một chút,",
            "Giữ nhịp học đều và mở rộng dần kiến thức Scratch,",
            "Chuyển sang các bài tập Scratch đa dạng hơn,",
        ],
        "high_weak": [
            "Nên dành thêm buổi ôn {weak} trên Scratch,",
            "Ưu tiên cải thiện {weak} trong các buổi học Scratch,",
            "Tập trung luyện {weak} qua bài thực hành Scratch,",
            "Dành 1–2 buổi/tuần cho phần {weak},",
        ],
        "mid": [
            "Theo lộ trình Scratch cơ bản, củng cố nền tảng,",
            "Tiếp tục Scratch cơ bản, ôn đều mỗi tuần,",
            "Học Scratch cơ bản — vững kiến thức rồi mới học sâu,",
            "Nên theo Scratch cơ bản, mỗi tuần luyện 2 buổi,",
        ],
        "low": [
            "Bắt đầu Scratch cơ bản, xây nền tảng từ đầu,",
            "Học Scratch cơ bản — nắm chắc kiến thức nền,",
        ],
        "beginner": [
            "Làm quen máy tính và lập trình Scratch từ thao tác cơ bản,",
            "Bắt đầu bằng làm quen máy tính, sau đó học Scratch từng bước,",
            "Dành thời gian quen máy tính trước khi học Scratch,",
            "Cho em làm quen thiết bị rồi mới vào các bài Scratch đơn giản,",
        ],
    },
    "python": {
        "high_none": [
            "Tiếp tục học Python với chủ đề mới,",
            "Duy trì luyện Python 2–3 buổi mỗi tuần,",
            "Thử sức với bài Python khó hơn một chút,",
            "Mở rộng dần kiến thức Python qua bài tập đa dạng,",
        ],
        "high_weak": [
            "Nên ôn thêm {weak} khi luyện Python,",
            "Ưu tiên cải thiện {weak} trong các buổi code,",
            "Dành thêm thời gian cho phần {weak},",
        ],
        "mid": [
            "Theo lộ trình Python cơ bản, củng cố nền tảng,",
            "Tiếp tục Python cơ bản, luyện đều mỗi tuần,",
            "Học Python cơ bản — vững nền rồi mới học sâu,",
        ],
        "low": [
            "Bắt đầu Python cơ bản, xây nền từ đầu,",
            "Học Python cơ bản — nắm chắc kiến thức nền tảng,",
        ],
    },
}

SCRATCH_BEGINNER_FOUNDATION = [
    "Tập dùng chuột, bàn phím và làm quen màn hình Scratch.",
    "Học mở Scratch, chọn nhân vật, bấm cờ xanh ▶️ chạy thử.",
    "Luyện thao tác máy tính cơ bản trước khi ghép khối.",
    "Cùng người hướng dẫn thao tác click, kéo thả khối lệnh.",
]

SCRATCH_BEGINNER_GROWTH = [
    "Bắt đầu từ cờ xanh ▶️, cho nhân vật di chuyển vài bước.",
    "Thử xoay, đổi trang phục nhân vật bằng khối đơn giản.",
    "Làm 1–2 bài Scratch dễ để quen tư duy lập trình.",
    "Ghép 3–4 khối lệnh tạo chương trình chạy được.",
]

HIGH_PROJECTS = {
    "scratch": [
        "Thử làm mini-game hoặc hoạt hình ngắn trên Scratch.",
        "Tự thiết kế nhân vật điều khiển bằng phím mũi tên.",
        "Làm project kết hợp vòng lặp và điều kiện.",
        "Sáng tạo câu chuyện ngắn bằng khối lệnh Scratch.",
    ],
    "python": [
        "Viết chương trình đoán số hoặc tính toán nhỏ.",
        "Làm bài tập Python kết hợp if/else và vòng lặp.",
        "Tự viết chương trình in bảng cửu chương.",
        "Thử code chương trình chào hỏi hoặc hỏi tên người dùng.",
    ],
}


def _is_scratch(course):
    return (course or "").lower() == "scratch"


def _course_key(course):
    return "scratch" if _is_scratch(course) else "python"


def _course_label(course):
    return "Scratch" if _is_scratch(course) else "Python"


def _skill_label(course):
    return "khối lệnh" if _is_scratch(course) else "dòng code"


def _cat_label(cat, course_key):
    mapping = SCRATCH_CATEGORY_VI if course_key == "scratch" else CATEGORY_VI
    return mapping.get(cat, cat)


def _pick(pool, seed, salt=0):
    if not pool:
        return ""
    return pool[_abs_idx(seed + salt, len(pool))]


def _abs_idx(seed, size):
    return abs(seed) % size if size else 0


def _analyze_details(details, test_id=None, student_name=None):
    total = len(details)
    correct = sum(1 for d in details if d.get("is_correct"))
    wrong = [d for d in details if not d.get("is_correct")]
    unanswered = [d for d in details if not d.get("answer_text")]

    cat_stats = {}
    level_stats = {"easy": [0, 0], "medium": [0, 0], "hard": [0, 0]}
    for d in details:
        cat = d.get("category") or "logic"
        cat_stats.setdefault(cat, {"ok": 0, "total": 0})
        cat_stats[cat]["total"] += 1
        if d.get("is_correct"):
            cat_stats[cat]["ok"] += 1
        lv = d.get("level") or "medium"
        if lv in level_stats:
            level_stats[lv][1] += 1
            if d.get("is_correct"):
                level_stats[lv][0] += 1

    weak = sorted(
        [(c, s) for c, s in cat_stats.items() if s["total"] and s["ok"] / s["total"] < 0.6],
        key=lambda x: x[1]["ok"] / x[1]["total"],
    )
    strong = sorted(
        [(c, s) for c, s in cat_stats.items() if s["total"] and s["ok"] / s["total"] >= 0.75],
        key=lambda x: -(x[1]["ok"] / x[1]["total"]),
    )

    hard = level_stats["hard"]
    name_seed = sum(ord(c) for c in (student_name or "")[:20])
    return {
        "total": total,
        "correct": correct,
        "wrong": wrong,
        "unanswered": unanswered,
        "weak": weak,
        "strong": strong,
        "hard_ok": hard[0],
        "hard_total": hard[1],
        "level_stats": level_stats,
        "cat_stats": cat_stats,
        "seed": correct * 17 + total * 11 + len(wrong) * 5 + len(unanswered) * 9
        + sum(ord(c) for c in str(test_id or "")[:12])
        + name_seed,
    }


def _weak_topics_phrase(weak, course_key, seed, max_items=2):
    if not weak:
        return ""
    labels = [_cat_label(cat, course_key) for cat, _ in weak[:max_items]]
    if len(labels) == 1:
        return labels[0]
    joins = [" và ", ", còn ", " cùng "]
    return labels[0] + _pick(joins, seed, 4) + labels[1]


def _strong_detail(strong, course_key, seed):
    if not strong:
        return ""
    parts = [
        f"{_cat_label(cat, course_key)} ({stats['ok']}/{stats['total']} câu)"
        for cat, stats in strong[:2]
    ]
    templates_one = [
        "em thể hiện tốt ở {p}",
        "điểm sáng của em là {p}",
        "em làm khá tốt phần {p}",
        "đáng khen ở {p}",
    ]
    templates_two = [
        "em làm tốt {a} và {b}",
        "nổi bật ở {a}, {b}",
        "em vững {a}, {b}",
    ]
    if len(parts) == 1:
        return _pick(templates_one, seed, 6).format(p=parts[0])
    t = _pick(templates_two, seed, 7)
    return t.format(a=parts[0], b=parts[1])


def _skill_closing(skill, seed):
    return _pick(
        [
            f", nên xem kỹ từng {skill} rồi mới chọn đáp án.",
            f"; hãy đọc hiểu từng {skill} trước khi làm bài.",
            f", cần đọc lại từng {skill} một cách cẩn thận.",
            f"; nhớ hình dung thứ tự {skill} trước khi trả lời.",
            f", đừng vội — đọc kỹ từng {skill} trước.",
        ],
        seed,
        11,
    )


def _has_some_foundation(analysis):
    total = analysis["total"]
    if total and analysis["correct"] / total >= 0.3:
        return True
    return bool(analysis["strong"])


def _is_scratch_beginner(course, score):
    return _is_scratch(course) and score < 60


def _focus_categories(analysis):
    weak = analysis["weak"]
    cats = list(analysis["cat_stats"].keys())
    if not weak:
        primary = _pick(cats, analysis["seed"], 20) if cats else "logic"
        secondary = _pick([c for c in cats if c != primary] or cats, analysis["seed"], 21)
        return primary, secondary
    primary = weak[0][0]
    if len(weak) > 1:
        secondary = weak[1][0]
    else:
        alts = [c for c in cats if c != primary]
        secondary = alts[_abs_idx(analysis["seed"] + 22, len(alts))] if alts else primary
    return primary, secondary


def _hint_bullet(hint_map, course_key, cat, seed, salt):
    pool = hint_map[course_key].get(cat, hint_map[course_key].get("logic", []))
    if isinstance(pool, str):
        pool = [pool]
    all_cats = list(hint_map[course_key].values())
    flat = [item for sub in all_cats for item in (sub if isinstance(sub, list) else [sub])]
    combined = pool + [_pick(flat, seed, salt + i) for i in range(2)]
    return _pick(combined, seed, salt)


def _general_remark_scratch_beginner(score, analysis):
    correct, total = analysis["correct"], analysis["total"]
    seed = analysis["seed"]

    if score < 50:
        openings = [
            f"Em chưa thành thạo máy tính và chưa có kiến thức Scratch ({correct}/{total} câu đúng)",
            f"Kết quả {score} điểm cho thấy em cần làm quen thêm với máy tính trước khi học Scratch",
            f"Với {correct}/{total} câu đúng, em nên bắt đầu từ thao tác máy tính cơ bản",
            f"Em chưa vững thao tác máy tính lẫn kiến thức Scratch ({correct}/{total} câu)",
        ]
    else:
        openings = [
            f"Em chưa có kiến thức Scratch ({correct}/{total} câu đúng)",
            f"Kết quả {score} điểm cho thấy em cần học Scratch từ nền tảng",
            f"Với {correct}/{total} câu đúng, em nên được hướng dẫn Scratch từng bước",
            f"Em chưa vững Scratch ({correct}/{total} câu) dù đã biết thao tác máy cơ bản",
        ]
    remark = _pick(openings, seed)
    remark += _pick(
        [
            ", cần người hướng dẫn từng bước ban đầu",
            ", nên được đồng hành sát sao trong những buổi đầu",
            ", cần thêm thời gian làm quen trước khi học sâu",
        ],
        seed,
        1,
    )

    if len(analysis["unanswered"]) >= 3:
        remark += _pick(
            [
                f". Em để trống {len(analysis['unanswered'])} câu — khi đã quen máy hơn hãy thử trả lời hết",
                f". Còn {len(analysis['unanswered'])} câu chưa làm — luyện thêm để tự tin hơn",
            ],
            seed,
            2,
        )

    remark += _skill_closing("khối lệnh", seed)
    return remark


def _general_remark_high(label, skill, score, analysis, course_key):
    correct, total = analysis["correct"], analysis["total"]
    strong_line = _strong_detail(analysis["strong"], course_key, analysis["seed"])
    weak_phrase = _weak_topics_phrase(analysis["weak"], course_key, analysis["seed"])
    hard_ok, hard_total = analysis["hard_ok"], analysis["hard_total"]
    seed = analysis["seed"]

    openings = [
        f"Em đạt {score} điểm ({correct}/{total} câu đúng) — kiến thức {label} khá vững",
        f"{correct}/{total} câu đúng cho thấy em nắm {label} tốt",
        f"Bài {label} {score} điểm — em đã có nền tảng khá chắc",
        f"Em làm khá tốt bài {label} với {correct}/{total} câu trả lời đúng",
        f"Kết quả {score} điểm phản ánh em hiểu {label} ở mức khá",
    ]
    remark = _pick(openings, seed)

    if strong_line:
        remark += f"; {strong_line}"

    if weak_phrase:
        remark += _pick(
            [
                f". Nên luyện thêm {weak_phrase}",
                f", phần {weak_phrase} có thể cải thiện thêm",
                f"; {weak_phrase} là hướng ôn tập phù hợp",
            ],
            seed,
            3,
        )
    else:
        remark += _pick(
            [
                ". Có thể thử thách bản thân với bài khó hơn",
                " và học thêm chủ đề mới",
                "; nên duy trì thói quen luyện tập đều",
            ],
            seed,
            4,
        )

    if hard_total:
        ratio = hard_ok / hard_total
        if ratio >= 0.85:
            remark += _pick(
                [
                    f"; phần câu khó rất tốt ({hard_ok}/{hard_total})",
                    f"; đặc biệt xử lý tốt câu khó ({hard_ok}/{hard_total})",
                ],
                seed,
                5,
            )
        elif ratio < 0.65:
            remark += f"; câu khó đúng {hard_ok}/{hard_total} — cần luyện thêm"

    remark += _skill_closing(skill, seed)
    return remark


def _general_remark_mid(label, skill, score, analysis, course_key):
    correct, total = analysis["correct"], analysis["total"]
    weak_phrase = _weak_topics_phrase(analysis["weak"], course_key, analysis["seed"])
    strong_line = _strong_detail(analysis["strong"], course_key, analysis["seed"])
    seed = analysis["seed"]

    openings = [
        f"Em có nền tảng {label} ({score} điểm, {correct}/{total} câu)",
        f"{correct}/{total} câu đúng — em đã biết {label} ở mức cơ bản",
        f"Em đạt {score} điểm {label}, kiến thức đang hình thành dần",
    ]
    remark = _pick(openings, seed)
    remark += _pick(
        [
            ", cần thêm thời gian củng cố cho vững",
            ", nên học thêm để nắm chắc hơn",
            ", cần luyện thêm để tiến bộ rõ",
        ],
        seed,
        1,
    )

    if weak_phrase:
        remark += _pick(
            [f", đặc biệt {weak_phrase}", f"; cần chú ý {weak_phrase}", f", phần {weak_phrase} cần ôn kỹ"],
            seed,
            2,
        )
    if strong_line:
        remark += f"; {strong_line}"

    remark += _skill_closing(skill, seed)
    return remark


def _general_remark_low(label, skill, score, analysis, course_key):
    correct, total = analysis["correct"], analysis["total"]
    weak_phrase = _weak_topics_phrase(analysis["weak"], course_key, analysis["seed"])
    strong_line = _strong_detail(analysis["strong"], course_key, analysis["seed"])
    seed = analysis["seed"]

    if _has_some_foundation(analysis):
        remark = _pick(
            [
                f"Em đã có chút nền tảng {label} ({correct}/{total} câu)",
                f"Dù {score} điểm, em vẫn bắt đầu quen {label}",
                f"Em có kiến thức {label} ban đầu ({correct}/{total} câu đúng)",
            ],
            seed,
        )
        remark += _pick(
            [", cần học thêm cho vững", ", nên ôn lại nền tảng kỹ hơn", ", cần thời gian củng cố"],
            seed,
            1,
        )
    else:
        remark = _pick(
            [
                f"Em mới làm quen {label} ({correct}/{total} câu đúng)",
                f"Em đang bắt đầu học {label} ({score} điểm)",
            ],
            seed,
        )
        remark += ", cần xây nền tảng từ đầu"

    if weak_phrase:
        remark += f", nhất là {weak_phrase}"
    if strong_line:
        remark += f"; {strong_line}"
    remark += _skill_closing(skill, seed)

    if len(analysis["unanswered"]) >= 3:
        remark += f" Em chưa làm {len(analysis['unanswered'])} câu — hãy thử trả lời hết khi đã tự tin hơn."
    return remark


def _general_remark(course, score, analysis):
    if _is_scratch_beginner(course, score):
        return _general_remark_scratch_beginner(score, analysis)

    label = _course_label(course)
    skill = _skill_label(course)
    course_key = _course_key(course)

    if score > 70:
        return _general_remark_high(label, skill, score, analysis, course_key)
    if score > 40 or _has_some_foundation(analysis):
        return _general_remark_mid(label, skill, score, analysis, course_key)
    return _general_remark_low(label, skill, score, analysis, course_key)


def _roadmap_opening(course_key, score, analysis):
    pools = ROADMAP_OPEN[course_key]
    seed = analysis["seed"]
    weak_phrase = _weak_topics_phrase(analysis["weak"], course_key, seed, 1)

    if score > 70:
        if analysis["weak"]:
            return _pick(pools["high_weak"], seed).format(weak=weak_phrase)
        return _pick(pools["high_none"], seed)

    if score > 40:
        return _pick(pools["mid"], seed)
    return _pick(pools["low"], seed)


def _roadmap_scratch_beginner(analysis):
    seed = analysis["seed"]
    return [
        _pick(ROADMAP_OPEN["scratch"]["beginner"], seed),
        _pick(SCRATCH_BEGINNER_FOUNDATION, seed, 1),
        _pick(SCRATCH_BEGINNER_GROWTH, seed, 2),
    ]


def _roadmap_bullets(course, score, analysis, test=None):
    if _is_scratch_beginner(course, score):
        return _roadmap_scratch_beginner(analysis)

    key = _course_key(course)
    primary, secondary = _focus_categories(analysis)
    seed = analysis["seed"]

    bullets = [
        _roadmap_opening(key, score, analysis),
        _hint_bullet(FOUNDATION_HINT, key, primary, seed, 30),
        _hint_bullet(GROWTH_HINT, key, secondary, seed, 40),
    ]

    if score > 70 and not analysis["weak"]:
        bullets[2] = _pick(HIGH_PROJECTS[key], seed, 50)

    return bullets


def generate_student_comment(test):
    course = test.get("course_name") or ""
    score = float(test.get("score") or 0)
    details = test.get("details") or []

    analysis = _analyze_details(details, test.get("id"), test.get("student_name"))
    remark = _general_remark(course, score, analysis)
    bullets = _roadmap_bullets(course, score, analysis, test)

    return (
        f"Nhận xét chung\n{remark}\n\n"
        f"Đề xuất lộ trình\n"
        + "\n".join(f"• {b}" for b in bullets)
    )
