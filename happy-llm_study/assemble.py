#!/usr/bin/env python3
"""Merge validated chapter cards into study_data.json for build_site.py."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(__file__).resolve().parent

chapters = []
for name in ["partA.json", "partB.json", "partC.json", "partD.json"]:
    chapters.extend(json.loads((OUT / "parts" / name).read_text(encoding="utf-8")))
chapters.sort(key=lambda c: c["id"])

data = {
    "book_title": "Happy-LLM：从零开始构建大模型",
    "author": "Datawhale 开源教程",
    "source_note": "解析自 happy-llm 仓库 Markdown 教程（docs 八章 + 前言/环境准备 + Extra-Chapter 七篇），逐章提炼，非原文全文",
    "overall_summary": (
        "《Happy-LLM》是 Datawhale 的 LLM 教程，按「原理 → 实现 → 应用 → 前沿」展开。"
        "前四章从 NLP 任务与文本表示讲到注意力、Transformer 与位置编码，对比 BERT、T5、GPT/LLaMA "
        "三类预训练架构，并给出 LLM 的涌现能力与 Pretrain–SFT–RLHF 范式。第五、六章动手："
        "从零实现 LLaMA2（RMSNorm、RoPE、GQA）、训练 BPE 分词器、预训练并微调小模型；"
        "再用 Transformers、DeepSpeed 走通 SFT 与 LoRA。第七章讲评测、RAG 与 Agent；"
        "第八章进入 Agentic RL，覆盖 GRPO、在线蒸馏、Search-R1 与 ReTool 的多轮工具 rollout。"
        "七篇拓展博客补充词元化、解码与思维预算等专题。全书强调理论落到代码："
        "按章配独立环境，先跑通小模型再扩规模。"
    ),
    "overall_takeaways": [
        "技术主线：文本表示 → 注意力/Transformer → 预训练语言模型 → 大语言模型，Decoder-Only 成为当代 LLM 主流架构。",
        "训练三段式：Pretrain 用海量文本学语言与知识，SFT 用指令数据学对话格式与任务能力，RLHF/RL 用偏好或可验证奖励对齐推理行为。",
        "实现抓手：RMSNorm + RoPE + GQA 构成的 LLaMA2 结构、BPE 分词器、SFT 的 loss_mask、Trainer/DeepSpeed 分布式训练与 LoRA/QLoRA 参数高效微调。",
        "应用落地：评测数据集与榜单判断能力边界，RAG 用向量库给模型补外部知识，Agent 靠工具调用把语言模型变成执行体。",
        "前沿的关键细节：GRPO 用组内相对优势省掉 Value Model，OPD 借 Reverse KL 提供逐 token 信号，多轮工具训练靠 observation mask 与 token 连续性保证梯度只落在模型动作上。",
        "学习方法：每章单独建环境，先在小模型和小数据上跑通全流程、看清数据形状，再逐步扩大规模并对照原文代码调试。",
    ],
    "chapters": chapters,
}

path = OUT / "study_data.json"
path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"已写入 {path}，{len(chapters)} 章，overall_summary {len(data['overall_summary'])} 字")
