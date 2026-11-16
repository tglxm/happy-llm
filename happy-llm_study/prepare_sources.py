#!/usr/bin/env python3
"""Turn the happy-llm repo's own chapter layout into ebook-study-site inputs.

Outputs:
  <outdir>/chapters.json
  <outdir>/sources/chNN.md

Long chapters are condensed per markdown section (heading + the leading prose
of that section), so the study notes cover the whole chapter instead of only
its first 20k characters. Code blocks are skipped; prose is kept verbatim.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
SRC = OUT / "sources"
SRC.mkdir(parents=True, exist_ok=True)

MAX_CHARS = 16000

# (id, title, category, files, note)
CHAPTERS = [
    ("01", "学习与环境准备", "导读", ["docs/学习与环境准备.md"], ""),
    ("02", "前言", "导读", ["docs/前言.md"], ""),
    ("03", "第一章 NLP 基础概念", "基础", ["docs/chapter1/第一章 NLP基础概念.md"], ""),
    ("04", "第二章 Transformer 架构", "基础", ["docs/chapter2/第二章 Transformer架构.md"], ""),
    ("05", "第三章 预训练语言模型", "基础", ["docs/chapter3/第三章 预训练语言模型.md"], ""),
    ("06", "第四章 大语言模型", "核心", ["docs/chapter4/第四章 大语言模型.md"], ""),
    ("07", "第五章 动手搭建大模型", "实战", ["docs/chapter5/第五章 动手搭建大模型.md"], ""),
    ("08", "第六章 大模型训练流程实践", "实战",
     ["docs/chapter6/第六章 大模型训练流程实践.md",
      "docs/chapter6/readme.md",
      "docs/chapter6/6.4[WIP] 偏好对齐.md"],
     "含第六章实践说明与 6.4 偏好对齐（WIP）"),
    ("09", "第七章 大模型应用", "实战", ["docs/chapter7/第七章 大模型应用.md"], ""),
    ("10", "第八章 大模型强化学习", "进阶",
     ["docs/chapter8/第八章 大模型强化学习.md",
      "docs/chapter8/grpo/README.md",
      "docs/chapter8/opd/README.md",
      "docs/chapter8/search-r1/README.md",
      "docs/chapter8/retool/README.md"],
     "含 GRPO / OPD / Search-R1 / ReTool 四个子项目说明"),
    ("11", "微调 0.6B 小模型有什么意义？", "拓展",
     ["Extra-Chapter/why-fine-tune-small-large-language-models/readme.md"], ""),
    ("12", "Transformer 整体模块设计解读", "拓展",
     ["Extra-Chapter/transformer-architecture/readme.md"], ""),
    ("13", "文本数据处理详解", "拓展",
     ["Extra-Chapter/text-data-processing/readme.md"], ""),
    ("14", "超小中文多模态模型的拼接微调", "拓展",
     ["Extra-Chapter/vlm-concatenation-finetune/README.md"], ""),
    ("15", "S1: Thinking Budget with vLLM", "拓展",
     ["Extra-Chapter/s1-vllm-thinking-budget/readme.md"], ""),
    ("16", "CDDRS：细粒度语义增强的 RAG 检索", "拓展",
     ["Extra-Chapter/CDDRS/readme.md"], ""),
    ("17", "大模型生成 Token 的方式有哪些？", "拓展",
     ["Extra-Chapter/generation-method/readme.md"], ""),
]

HEAD_RE = re.compile(r"^(#{1,4})\s+(.*)$")
IMG_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")


def clean_line(line: str) -> str:
    line = IMG_RE.sub("", line)
    line = LINK_RE.sub(r"\1", line)
    line = re.sub(r"<[^>]+>", "", line)          # html tags
    line = re.sub(r"`{1,3}", "", line)            # inline code fences
    line = re.sub(r"\s{2,}", " ", line)
    return line.strip()


def is_noise(line: str) -> bool:
    if not line:
        return True
    if re.fullmatch(r"[|:\-=\s]+", line):        # table dividers
        return True
    if re.fullmatch(r"https?://\S+", line):
        return True
    if re.fullmatch(r"[*_~]{2,}", line):
        return True
    return False


def sections_from(text: str):
    """Return [(heading, prose)] with code blocks removed."""
    sections, cur_title, cur = [], "开篇", []
    in_code = False
    for raw in text.split("\n"):
        line = raw.replace("\r", "")
        if line.lstrip().startswith(("```", "~~~")):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = HEAD_RE.match(line.strip())
        if m:
            if cur:
                sections.append((cur_title, "\n".join(cur).strip()))
            cur_title = ("  " * (len(m.group(1)) - 2)) + m.group(2).strip()
            cur = []
            continue
        c = clean_line(line)
        if is_noise(c):
            continue
        cur.append(c)
    if cur:
        sections.append((cur_title, "\n".join(cur).strip()))
    return [(t, p) for t, p in sections if p]


def condense(files, budget):
    all_sections = []
    for rel in files:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8", errors="ignore")
        secs = sections_from(text)
        if len(files) > 1:
            all_sections.append(("### [附] " + rel, ""))
        all_sections.extend(secs)

    # outline first
    outline = "\n".join(f"- {t.strip()}" for t, _ in all_sections if t.strip())
    # proportional per-section allowance
    total = sum(len(p) for _, p in all_sections)
    per = max(220, min(1100, (budget - 2200) // max(1, len(all_sections))))
    if total > budget - 2200:
        per = max(200, (budget - 2200) // max(1, len(all_sections)))

    blocks = []
    for title, prose in all_sections:
        if not title.strip():
            continue
        snippet = prose[:per]
        if len(prose) > per:
            snippet = snippet.rsplit("。", 1)[0] + "。" if "。" in snippet else snippet
            snippet += " …"
        blocks.append(f"## {title.strip()}\n{snippet}" if snippet else f"## {title.strip()}")
    body = "\n\n".join(blocks)
    return f"# 章节大纲（原文标题）\n\n{outline}\n\n# 原文分节摘录（逐字节选，代码已省略）\n\n{body}\n"


def main():
    meta = {
        "book_title": "Happy-LLM：从零开始构建大模型",
        "author": "Datawhale",
        "source_file": "D:/Source/dataLearn/happy-llm (Markdown 教程仓库)",
        "format": "md",
        "chapters": [],
    }
    for cid, title, cat, files, note in CHAPTERS:
        missing = [f for f in files if not (ROOT / f).exists()]
        if missing:
            print(f"缺少文件: {missing}", file=sys.stderr)
            sys.exit(1)
        raw_len = sum((ROOT / f).stat().st_size for f in files)
        text = condense(files, MAX_CHARS)
        src = f"sources/ch{cid}.md"
        (OUT / src).write_text(text, encoding="utf-8")
        meta["chapters"].append({
            "id": cid,
            "title": title,
            "category": cat,
            "chars": len(text),
            "raw_bytes": raw_len,
            "truncated": True,
            "source": src,
            "source_note": note,
            "files": files,
        })
        print(f"ch{cid} {title[:24]:<26} 原文 {raw_len:>7} B -> 摘录 {len(text):>6} 字符, "
              f"{len([l for l in text.splitlines() if l.startswith('## ')])} 节")
    (OUT / "chapters.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n完成：{len(meta['chapters'])} 章 -> {OUT}")


if __name__ == "__main__":
    main()
