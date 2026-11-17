"""Chấm bài Scratch theo cấu trúc khối (so khớp cây opcode với đáp án mẫu)."""

from __future__ import annotations

import ast
import json
import math
import re
from typing import Any


def _norm_expr(raw: Any) -> str:
    s = str(raw if raw is not None else "").strip().lower()
    s = s.replace("×", "*").replace("÷", "/").replace(" ", "")
    s = s.replace("π", "3.14").replace("pi", "3.14")
    return s


def _eval_expr(raw: Any):
    """Thử tính số; thất bại thì trả về chuỗi đã chuẩn hóa."""
    s = _norm_expr(raw)
    if not s:
        return ""
    try:
        tree = ast.parse(s, mode="eval")
        for node in ast.walk(tree):
            if not isinstance(
                node,
                (
                    ast.Expression,
                    ast.BinOp,
                    ast.UnaryOp,
                    ast.Constant,
                    ast.Num,
                    ast.Add,
                    ast.Sub,
                    ast.Mult,
                    ast.Div,
                    ast.Pow,
                    ast.USub,
                    ast.UAdd,
                    ast.Mod,
                    ast.FloorDiv,
                ),
            ):
                return s
        val = eval(compile(tree, "<expr>", "eval"), {"__builtins__": {}}, {})
        if isinstance(val, (int, float)) and math.isfinite(val):
            return round(float(val), 6)
    except Exception:
        pass
    return s


def _expr_equal(a: Any, b: Any) -> bool:
    ea, eb = _eval_expr(a), _eval_expr(b)
    if isinstance(ea, float) and isinstance(eb, float):
        return abs(ea - eb) < 1e-3
    return str(ea) == str(eb)


# Map alias → opcode chuẩn
OP_ALIASES = {
    "whenflagclicked": "when_flag",
    "event_whenflagclicked": "when_flag",
    "when_green_flag": "when_flag",
    "khi_bam_co": "when_flag",
    "whenkeypressed": "when_key",
    "event_whenkeypressed": "when_key",
    "khi_nhan_phim": "when_key",
    "motion_movesteps": "move",
    "di_chuyen": "move",
    "move_steps": "move",
    "motion_turnright": "turn_right",
    "xoay_phai": "turn_right",
    "turnright": "turn_right",
    "motion_turnleft": "turn_left",
    "xoay_trai": "turn_left",
    "control_repeat": "repeat",
    "lap_lai": "repeat",
    "control_forever": "forever",
    "lap_mai": "forever",
    "pen_pendown": "pen_down",
    "dat_but_xuong": "pen_down",
    "pen_penup": "pen_up",
    "pen_clear": "pen_clear",
    "xoa_tat_ca": "pen_clear",
    "pen_setpencolorto": "pen_color",
    "dat_mau_but": "pen_color",
    "pen_setpensizeto": "pen_size",
    "dat_co_but": "pen_size",
    "motion_gotoxy": "goto_xy",
    "di_toi_xy": "goto_xy",
    "motion_pointtowards": "point_towards",
    "huong_ve": "point_towards",
    "motion_glidesecstoxy": "glide",
    "sensing_touchingobject": "touching",
    "sound_play": "play_sound",
    "play_sound_until_done": "play_sound",
    "phat_am_thanh": "play_sound",
    "sound_playdrum": "play_note",
    "play_note": "play_note",
    "phat_not": "play_note",
    "looks_say": "say",
    "motion_changexby": "change_x",
    "motion_changeyby": "change_y",
    "motion_setx": "set_x",
    "motion_sety": "set_y",
    "sensing_mousedown": "mouse_down",
    "goto_mouse": "goto_mouse",
    "di_toi_con_tro": "goto_mouse",
    "point_towards_mouse": "point_mouse",
    "huong_ve_con_tro": "point_mouse",
    "move_towards_mouse": "move_towards_mouse",
}


def normalize_op(op: Any) -> str:
    s = str(op or "").strip().lower().replace(" ", "_").replace("-", "_")
    return OP_ALIASES.get(s, s)


def normalize_block(block: Any) -> dict | None:
    if block is None:
        return None
    if isinstance(block, str):
        return {"op": normalize_op(block)}
    if not isinstance(block, dict):
        return None
    op = normalize_op(block.get("op") or block.get("opcode") or block.get("type"))
    if not op:
        return None
    out: dict[str, Any] = {"op": op}

    # Tham số theo loại
    if op in ("move",):
        out["steps"] = _eval_expr(block.get("steps") if "steps" in block else block.get("value"))
    elif op in ("turn_right", "turn_left"):
        out["degrees"] = _eval_expr(
            block.get("degrees") if "degrees" in block else block.get("value")
        )
    elif op == "repeat":
        out["times"] = _eval_expr(block.get("times") if "times" in block else block.get("value"))
        out["body"] = normalize_script(block.get("body") or block.get("substack") or [])
    elif op == "forever":
        out["body"] = normalize_script(block.get("body") or block.get("substack") or [])
    elif op == "when_key":
        key = str(block.get("key") or block.get("value") or "").strip().lower()
        out["key"] = key
    elif op == "pen_color":
        out["color"] = _norm_expr(block.get("color") or block.get("value") or "")
    elif op == "pen_size":
        out["size"] = _eval_expr(block.get("size") if "size" in block else block.get("value"))
    elif op == "goto_xy":
        out["x"] = _eval_expr(block.get("x"))
        out["y"] = _eval_expr(block.get("y"))
    elif op in ("play_sound", "play_note"):
        out["sound"] = _norm_expr(block.get("sound") or block.get("note") or block.get("value") or "")
    elif op == "say":
        out["text"] = str(block.get("text") or block.get("value") or "").strip().lower()
    elif op in ("change_x", "change_y", "set_x", "set_y"):
        out["value"] = _eval_expr(block.get("value") if "value" in block else block.get("steps"))
    elif op == "point_towards":
        out["target"] = _norm_expr(block.get("target") or block.get("value") or "mouse")
    else:
        # Giữ args phụ nếu có
        for k, v in block.items():
            if k in ("op", "opcode", "type", "body", "substack", "id"):
                continue
            if isinstance(v, (list, dict)):
                continue
            out[k] = _norm_expr(v) if isinstance(v, str) else _eval_expr(v)

    return out


def normalize_script(blocks: Any) -> list:
    if not isinstance(blocks, list):
        return []
    out = []
    for b in blocks:
        nb = normalize_block(b)
        if nb:
            out.append(nb)
    return out


def normalize_project(project: Any) -> list:
    """
    Trả về list script chuẩn hóa:
    [{ "sprite": str, "hat": str, "key": ?, "body": [...] }, ...]
    Sắp xếp ổn định để so khớp.
    """
    if isinstance(project, str):
        try:
            project = json.loads(project)
        except Exception:
            return []

    scripts = []
    if isinstance(project, dict) and "sprites" in project:
        for sp in project.get("sprites") or []:
            name = str(sp.get("name") or "Sprite1")
            for sc in sp.get("scripts") or []:
                hat = normalize_op(sc.get("hat") or "when_flag")
                body = normalize_script(sc.get("body") or sc.get("blocks") or [])
                item = {"sprite": name.lower(), "hat": hat, "body": body}
                if hat == "when_key":
                    item["key"] = str(sc.get("key") or "").strip().lower()
                scripts.append(item)
    elif isinstance(project, dict) and "scripts" in project:
        for sc in project.get("scripts") or []:
            hat = normalize_op(sc.get("hat") or "when_flag")
            body = normalize_script(sc.get("body") or sc.get("blocks") or [])
            item = {
                "sprite": str(sc.get("sprite") or "sprite1").lower(),
                "hat": hat,
                "body": body,
            }
            if hat == "when_key":
                item["key"] = str(sc.get("key") or "").strip().lower()
            scripts.append(item)
    elif isinstance(project, list):
        # Chỉ một thân script
        scripts.append({"sprite": "sprite1", "hat": "when_flag", "body": normalize_script(project)})

    def sort_key(s):
        return (s.get("hat") or "", s.get("key") or "", s.get("sprite") or "", json.dumps(s.get("body"), sort_keys=True))

    scripts.sort(key=sort_key)
    return scripts


def _blocks_equal(a: dict, b: dict) -> bool:
    if a.get("op") != b.get("op"):
        return False
    op = a["op"]
    if op == "move":
        return _expr_equal(a.get("steps"), b.get("steps"))
    if op in ("turn_right", "turn_left"):
        return _expr_equal(a.get("degrees"), b.get("degrees"))
    if op == "repeat":
        return _expr_equal(a.get("times"), b.get("times")) and _script_equal(a.get("body"), b.get("body"))
    if op == "forever":
        return _script_equal(a.get("body"), b.get("body"))
    if op == "pen_color":
        ca = _norm_expr(a.get("color"))
        cb = _norm_expr(b.get("color"))
        aliases = {
            "red": {"red", "đỏ", "do", "#ff0000", "#f00", "ff0000"},
            "blue": {"blue", "xanh", "xanhduong", "#0000ff"},
            "green": {"green", "xanhlá", "xanhla", "#00ff00"},
        }
        for group in aliases.values():
            if ca in group and cb in group:
                return True
        return ca == cb or _expr_equal(a.get("color"), b.get("color"))
    if op == "pen_size":
        return _expr_equal(a.get("size"), b.get("size"))
    if op == "goto_xy":
        return _expr_equal(a.get("x"), b.get("x")) and _expr_equal(a.get("y"), b.get("y"))
    if op in ("play_sound", "play_note"):
        return _norm_expr(a.get("sound")) == _norm_expr(b.get("sound"))
    if op == "when_key":
        return True  # key so ở cấp script
    if op in ("change_x", "change_y", "set_x", "set_y"):
        return _expr_equal(a.get("value"), b.get("value"))
    if op == "point_towards":
        ta = _norm_expr(a.get("target") or "mouse")
        tb = _norm_expr(b.get("target") or "mouse")
        return ta in ("mouse", "con_tro", "pointer", "_mouse_") or ta == tb
    # Ops không tham số
    return True


def _strip_optional(blocks: list | None) -> list:
    """Bỏ khối phụ không ảnh hưởng đáp án chính (xóa tất cả, nhấc bút…)."""
    skip = {"pen_clear", "pen_up"}
    return [b for b in (blocks or []) if b.get("op") not in skip]


def _script_equal(a: list | None, b: list | None) -> bool:
    aa = _strip_optional(a)
    bb = _strip_optional(b)
    if len(aa) != len(bb):
        return False
    return all(_blocks_equal(x, y) for x, y in zip(aa, bb))


def _script_match(student: dict, expected: dict) -> bool:
    if student.get("hat") != expected.get("hat"):
        return False
    if expected.get("hat") == "when_key":
        if (student.get("key") or "") != (expected.get("key") or ""):
            return False
    # Sprite name: nếu expected có ràng buộc cụ thể (không phải *) thì so
    exp_sp = expected.get("sprite") or "*"
    if exp_sp not in ("*", "") and student.get("sprite") != exp_sp:
        # Cho phép khớp nếu cùng vai trò — nới: bỏ qua tên sprite trừ khi bắt buộc
        pass
    return _script_equal(student.get("body"), expected.get("body"))


def describe_block(b: dict) -> str:
    op = b.get("op")
    if op == "move":
        return f"di chuyển ({b.get('steps')}) bước"
    if op == "turn_right":
        return f"xoay phải ({b.get('degrees')}) độ"
    if op == "turn_left":
        return f"xoay trái ({b.get('degrees')}) độ"
    if op == "repeat":
        return f"lặp lại ({b.get('times')}) lần {{...}}"
    if op == "forever":
        return "lặp lại mãi {...}"
    if op == "pen_down":
        return "đặt bút xuống"
    if op == "pen_up":
        return "nhấc bút lên"
    if op == "pen_clear":
        return "xóa tất cả"
    if op == "pen_color":
        return f"đặt màu bút ({b.get('color')})"
    if op == "pen_size":
        return f"đặt cỡ bút ({b.get('size')})"
    if op == "goto_mouse":
        return "đi tới con trỏ chuột"
    if op == "point_mouse":
        return "hướng về con trỏ chuột"
    if op == "play_note":
        return f"phát nốt ({b.get('sound')})"
    if op == "play_sound":
        return f"phát âm thanh ({b.get('sound')})"
    return op or "?"


def grade_project(student_project: Any, expected_project: Any) -> dict:
    """
    So khớp: mọi script trong expected phải có script student tương ứng.
    Student có thể có script thừa (bỏ qua).
    """
    stu = normalize_project(student_project)
    exp = normalize_project(expected_project)

    if not exp:
        return {"correct": False, "message": "Đáp án mẫu trống", "mismatches": ["missing_solution"]}

    mismatches = []
    used = set()
    for i, e in enumerate(exp):
        found = False
        for j, s in enumerate(stu):
            if j in used:
                continue
            if _script_match(s, e):
                used.add(j)
                found = True
                break
        if not found:
            label = e.get("hat")
            if e.get("hat") == "when_key":
                label = f"khi nhấn phím {e.get('key')}"
            elif e.get("hat") == "when_flag":
                label = "khi bấm cờ xanh"
            body_desc = " → ".join(describe_block(b) for b in (e.get("body") or [])[:6])
            mismatches.append(f"Thiếu hoặc sai script «{label}»: {body_desc}")

    correct = len(mismatches) == 0
    return {
        "correct": correct,
        "message": "Chính xác! Khối lệnh khớp đáp án." if correct else "Chưa khớp đáp án mẫu.",
        "mismatches": mismatches,
        "student_scripts": len(stu),
        "expected_scripts": len(exp),
    }
