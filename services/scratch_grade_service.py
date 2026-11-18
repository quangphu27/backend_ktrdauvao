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


def _is_blank(raw: Any) -> bool:
    if raw is None:
        return True
    if isinstance(raw, str) and not raw.strip():
        return True
    return False


def _expr_equal(a: Any, b: Any) -> bool:
    """So khớp giá trị: trống ≠ đáp án; số chấp nhận sai số nhỏ; chuỗi sau chuẩn hóa."""
    if _is_blank(a) and not _is_blank(b):
        return False
    if _is_blank(b) and not _is_blank(a):
        return False
    if _is_blank(a) and _is_blank(b):
        return True
    ea, eb = _eval_expr(a), _eval_expr(b)
    if isinstance(ea, float) and isinstance(eb, float):
        return abs(ea - eb) < 1e-3
    return str(ea) == str(eb)


def _fmt_val(raw: Any) -> str:
    if _is_blank(raw):
        return "(trống)"
    ev = _eval_expr(raw)
    return str(ev)


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


def _color_equal(a: Any, b: Any) -> bool:
    ca = _norm_expr(a)
    cb = _norm_expr(b)
    if not ca and not cb:
        return True
    if not ca or not cb:
        return False
    aliases = {
        "red": {"red", "đỏ", "do", "#ff0000", "#f00", "ff0000"},
        "blue": {"blue", "xanh", "xanhduong", "#0000ff"},
        "green": {"green", "xanhlá", "xanhla", "#00ff00"},
    }
    for group in aliases.values():
        if ca in group and cb in group:
            return True
    return ca == cb or _expr_equal(a, b)


def _blocks_equal(a: dict, b: dict) -> bool:
    return not _diff_blocks(a, b, "")


def _diff_blocks(stu: dict, exp: dict, path: str) -> list[str]:
    """So từng khối/ô số; trả về danh sách lệch (rỗng = khớp)."""
    errs: list[str] = []
    if stu.get("op") != exp.get("op"):
        return [f"{path}: sai khối (em «{describe_block(stu)}», đáp án «{describe_block(exp)}»)"]
    op = exp["op"]
    label = describe_block(exp)

    def check(field_label: str, got: Any, want: Any, equal_fn=None):
        ok = (equal_fn or _expr_equal)(got, want)
        if not ok:
            errs.append(
                f"{path}{label} — {field_label}: em điền {_fmt_val(got)}, đáp án {_fmt_val(want)}"
            )

    if op == "move":
        check("bước", stu.get("steps"), exp.get("steps"))
    elif op in ("turn_right", "turn_left"):
        check("độ", stu.get("degrees"), exp.get("degrees"))
    elif op == "repeat":
        check("số lần", stu.get("times"), exp.get("times"))
        errs.extend(_diff_script(stu.get("body"), exp.get("body"), path + "lặp›"))
    elif op == "forever":
        errs.extend(_diff_script(stu.get("body"), exp.get("body"), path + "mãi›"))
    elif op == "pen_color":
        check("màu", stu.get("color"), exp.get("color"), _color_equal)
    elif op == "pen_size":
        check("cỡ", stu.get("size"), exp.get("size"))
    elif op == "goto_xy":
        check("x", stu.get("x"), exp.get("x"))
        check("y", stu.get("y"), exp.get("y"))
    elif op in ("play_sound", "play_note"):
        check("nốt/âm", stu.get("sound"), exp.get("sound"))
    elif op in ("change_x", "change_y", "set_x", "set_y"):
        check("giá trị", stu.get("value"), exp.get("value"))
    elif op == "point_towards":
        ta = _norm_expr(stu.get("target") or "mouse")
        tb = _norm_expr(exp.get("target") or "mouse")
        if not (ta in ("mouse", "con_tro", "pointer", "_mouse_") or ta == tb):
            errs.append(f"{path}{label}: sai đích")
    # Ops không tham số (pen_down, goto_mouse, point_mouse…): khớp opcode là đủ
    return errs


def _strip_optional(blocks: list | None) -> list:
    """Bỏ khối phụ không ảnh hưởng đáp án chính (xóa tất cả, nhấc bút…)."""
    skip = {"pen_clear", "pen_up"}
    return [b for b in (blocks or []) if b.get("op") not in skip]


def _diff_script(a: list | None, b: list | None, path: str = "") -> list[str]:
    aa = _strip_optional(a)
    bb = _strip_optional(b)
    if len(aa) != len(bb):
        return [f"{path}: số khối khác (em {len(aa)}, đáp án {len(bb)})"]
    errs: list[str] = []
    for i, (x, y) in enumerate(zip(aa, bb)):
        errs.extend(_diff_blocks(x, y, f"{path}[{i}] "))
    return errs


def _script_equal(a: list | None, b: list | None) -> bool:
    return not _diff_script(a, b)


def _script_match(student: dict, expected: dict) -> bool:
    return not _diff_script_match(student, expected)


def _diff_script_match(student: dict, expected: dict) -> list[str]:
    if student.get("hat") != expected.get("hat"):
        return [f"Sai sự kiện bắt đầu (em {student.get('hat')}, đáp án {expected.get('hat')})"]
    if expected.get("hat") == "when_key":
        if (student.get("key") or "") != (expected.get("key") or ""):
            return [
                f"Sai phím (em {student.get('key') or '(trống)'}, đáp án {expected.get('key')})"
            ]
    return _diff_script(student.get("body"), expected.get("body"), "")


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


def project_has_filled_fields(project: Any) -> bool:
    """True nếu mọi ô số/trường trong project đều đã điền (không trống)."""
    scripts = normalize_project(project)
    if not scripts:
        return False

    def walk(blocks: list) -> bool:
        for b in blocks or []:
            op = b.get("op")
            if op == "move" and _is_blank(b.get("steps")):
                return False
            if op in ("turn_right", "turn_left") and _is_blank(b.get("degrees")):
                return False
            if op == "repeat":
                if _is_blank(b.get("times")):
                    return False
                if not walk(b.get("body") or []):
                    return False
            elif op == "forever":
                if not walk(b.get("body") or []):
                    return False
            elif op == "pen_color" and _is_blank(b.get("color")):
                return False
            elif op == "pen_size" and _is_blank(b.get("size")):
                return False
            elif op in ("play_note", "play_sound") and _is_blank(b.get("sound")):
                return False
        return True

    return all(walk(s.get("body") or []) for s in scripts)


def grade_project(student_project: Any, expected_project: Any) -> dict:
    """
    Chấm chặt: mỗi script đáp án phải khớp cấu trúc + từng ô số/trường.
    Ô trống hoặc sai giá trị → không đúng. Script thừa của HS bị bỏ qua.
    """
    stu = normalize_project(student_project)
    exp = normalize_project(expected_project)

    if not exp:
        return {"correct": False, "message": "Đáp án mẫu trống", "mismatches": ["missing_solution"]}

    if not stu:
        return {
            "correct": False,
            "message": "Chưa làm bài Scratch.",
            "mismatches": ["empty_project"],
            "student_scripts": 0,
            "expected_scripts": len(exp),
        }

    mismatches: list[str] = []
    used = set()
    for e in exp:
        label = e.get("hat")
        if e.get("hat") == "when_key":
            label = f"khi nhấn phím {e.get('key')}"
        elif e.get("hat") == "when_flag":
            label = "khi bấm cờ xanh"

        best_errs = None
        best_j = None
        for j, s in enumerate(stu):
            if j in used:
                continue
            # Ưu tiên cùng hat (+ key)
            if s.get("hat") != e.get("hat"):
                continue
            if e.get("hat") == "when_key" and (s.get("key") or "") != (e.get("key") or ""):
                continue
            errs = _diff_script_match(s, e)
            if not errs:
                best_errs = []
                best_j = j
                break
            if best_errs is None or len(errs) < len(best_errs):
                best_errs = errs
                best_j = j

        if best_errs is not None and len(best_errs) == 0 and best_j is not None:
            used.add(best_j)
            continue

        if best_errs:
            for err in best_errs[:4]:
                mismatches.append(f"«{label}» {err}")
            if best_j is not None:
                used.add(best_j)
        else:
            body_desc = " → ".join(describe_block(b) for b in (e.get("body") or [])[:6])
            mismatches.append(f"Thiếu script «{label}»: {body_desc}")

    correct = len(mismatches) == 0
    return {
        "correct": correct,
        "message": (
            "Chính xác! Khối lệnh và số liệu khớp đáp án."
            if correct
            else "Chưa đúng — kiểm tra lại từng ô số / nốt đã điền."
        ),
        "mismatches": mismatches,
        "student_scripts": len(stu),
        "expected_scripts": len(exp),
    }
