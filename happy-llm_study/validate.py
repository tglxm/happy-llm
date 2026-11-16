#!/usr/bin/env python3
"""Independently validate the four part files against chapters.json and sources."""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(__file__).resolve().parent
meta = json.loads((OUT / "chapters.json").read_text(encoding="utf-8"))
by_id = {c["id"]: c for c in meta["chapters"]}

parts = []
for name in ["partA.json", "partB.json", "partC.json", "partD.json"]:
    p = OUT / "parts" / name
    if not p.exists():
        print(f"缺失 {name}")
        sys.exit(1)
    parts.extend(json.loads(p.read_text(encoding="utf-8")))

errors, warns = [], []
seen = set()
for ch in parts:
    cid = ch.get("id")
    if cid in seen:
        errors.append(f"重复 id {cid}")
    seen.add(cid)
    ref = by_id.get(cid)
    if not ref:
        errors.append(f"id {cid} 不在 chapters.json")
        continue
    for f in ("title", "category"):
        if ch.get(f) != ref[f]:
            errors.append(f"ch{cid} {f} 不一致: {ch.get(f)!r} != {ref[f]!r}")
    s = ch.get("summary", "")
    if not (100 <= len(s) <= 400):
        warns.append(f"ch{cid} summary 长度 {len(s)}")
    kp = ch.get("key_points") or []
    if not (3 <= len(kp) <= 6):
        errors.append(f"ch{cid} key_points 数量 {len(kp)}")
    # quotes must be verbatim substrings of the excerpt section
    src = (OUT / ref["source"]).read_text(encoding="utf-8")
    excerpt = src.split("# 原文分节摘录", 1)[-1]
    excerpt_norm = re.sub(r"\s+", "", excerpt)
    for q in ch.get("quotes") or []:
        if len(q) > 100:
            errors.append(f"ch{cid} 引用超 100 字: {len(q)}")
        if re.sub(r"\s+", "", q) not in excerpt_norm:
            errors.append(f"ch{cid} 引用非原文逐字: {q[:45]}...")
    # quiz
    quiz = ch.get("quiz") or []
    if not (1 <= len(quiz) <= 3):
        errors.append(f"ch{cid} quiz 数量 {len(quiz)}")
    for i, q in enumerate(quiz):
        t = q.get("type", "choice")
        if not q.get("q"):
            errors.append(f"ch{cid} Q{i+1} 缺题干")
        if t == "choice":
            opts = q.get("options") or []
            a = q.get("answer")
            if len(opts) < 2:
                errors.append(f"ch{cid} Q{i+1} 选项不足")
            if not isinstance(a, int) or not (0 <= a < len(opts)):
                errors.append(f"ch{cid} Q{i+1} answer 非法: {a!r}")
        elif t == "reveal":
            if not q.get("a"):
                errors.append(f"ch{cid} Q{i+1} 缺参考答案")
        else:
            errors.append(f"ch{cid} Q{i+1} 未知题型 {t}")

missing = set(by_id) - seen
if missing:
    errors.append(f"缺少章节: {sorted(missing)}")

print(f"章节数 {len(parts)} / {len(by_id)}，自测题 {sum(len(c.get('quiz') or []) for c in parts)} 道，"
      f"金句 {sum(len(c.get('quotes') or []) for c in parts)} 条")
print(f"错误 {len(errors)}，警告 {len(warns)}")
for e in errors:
    print("  [ERR]", e)
for w in warns:
    print("  [WARN]", w)
