from __future__ import annotations

import re
from collections import Counter
from typing import Any

from .llm import configured_provider
from .parser import DocumentBlock
from .utils import compact, first_sentence, now_iso


AI_TERMS = [
    "attention",
    "transformer",
    "retrieval",
    "rerank",
    "rag",
    "adapter",
    "lora",
    "prefix",
    "preference",
    "rlhf",
    "dpo",
    "agent",
    "tool",
    "react",
    "clip",
    "llava",
    "benchmark",
    "evaluation",
    "alignment",
    "policy",
    "reward",
    "loss",
    "embedding",
    "encoder",
    "decoder",
]


def generate_paper_ir(metadata: dict[str, Any], blocks: list[DocumentBlock]) -> dict[str, Any]:
    provider = configured_provider()
    if provider is not None:
        try:
            # The LLM path is intentionally narrow in v1: it may enrich the same
            # IR shape, but never bypasses anchors or verification.
            return _llm_extract(provider, metadata, blocks)
        except Exception:
            pass
    return HeuristicExtractor(metadata, blocks).extract()


def _llm_extract(provider: Any, metadata: dict[str, Any], blocks: list[DocumentBlock]) -> dict[str, Any]:
    sample = [
        {
            "block_id": b.block_id,
            "type": b.type,
            "page": b.page,
            "section": b.section,
            "anchor_id": b.anchor_id,
            "content": compact(b.content, 700),
        }
        for b in blocks[:160]
    ]
    system = (
        "你是知微的论文 IR 抽取器。只输出严格 JSON。"
        "所有生成字段必须引用已有 anchor_id；不知道写 unknown；推测必须标 confidence。"
    )
    user = {
        "metadata": metadata,
        "document_blocks": sample,
        "task": "生成 AI/LLM/机器学习 method paper 的 Paper IR。不要编造没有 anchor 的结论。",
    }
    ir = provider.complete_json(system, str(user), {})
    ir.setdefault("metadata", metadata)
    return ir


class HeuristicExtractor:
    def __init__(self, metadata: dict[str, Any], blocks: list[DocumentBlock]):
        self.metadata = metadata
        self.blocks = blocks
        self.by_section: dict[str, list[DocumentBlock]] = {}
        for block in blocks:
            self.by_section.setdefault(block.section or "Unknown", []).append(block)

    def extract(self) -> dict[str, Any]:
        anchors = self._anchors()
        skeleton = self._skeleton()
        method_graph = self._method_graph(skeleton)
        method_delta = self._method_delta()
        formula_ir = self._formula_ir()
        experiment_matrix = self._experiment_matrix()
        claim_evidence = self._claim_evidence(experiment_matrix)
        glossary = self._glossary()
        reproduction = self._reproduction()
        return {
            "schema_version": "0.1.0",
            "generated_at": now_iso(),
            "generation_mode": "heuristic_grounded_v1",
            "scope": {
                "supported_domain": "AI / LLM / machine learning method paper",
                "unsupported_domains": ["medical", "materials", "mechanical", "control", "pure_math", "general_social_science"],
            },
            "metadata": self.metadata | {"uploaded_at": self.metadata.get("uploaded_at", now_iso())},
            "anchors": anchors,
            "paper_skeleton": skeleton,
            "method_graph": method_graph,
            "method_delta": method_delta,
            "formula_ir": formula_ir,
            "experiment_matrix": experiment_matrix,
            "claim_evidence_map": claim_evidence,
            "glossary": glossary,
            "reproduction_roadmap": reproduction,
            "visual_state": {
                "default_module": "structure",
                "layout": "three_column",
            },
        }

    def _anchors(self) -> list[dict[str, Any]]:
        return [
            {
                "anchor_id": block.anchor_id,
                "page": block.page,
                "section": block.section,
                "bbox": block.bbox,
                "text_span": compact(block.content, 900),
                "source_type": source_type(block.type),
            }
            for block in self.blocks
        ]

    def _section_text(self, names: list[str], limit_blocks: int = 5) -> tuple[str, list[str]]:
        selected: list[DocumentBlock] = []
        for name in names:
            selected.extend([b for b in self.by_section.get(name, []) if b.type in {"paragraph", "formula", "caption"}])
        if not selected:
            selected = [b for b in self.blocks if b.type == "paragraph"][:limit_blocks]
        selected = selected[:limit_blocks]
        text = " ".join(b.content for b in selected)
        return compact(text, 560) or "unknown", [b.anchor_id for b in selected[:4]]

    def _skeleton(self) -> dict[str, Any]:
        problem, problem_anchors = self._section_text(["Abstract", "Introduction"], 4)
        motivation, motivation_anchors = self._find_sentences(["motivat", "challenge", "problem", "limitation", "however"], ["Introduction", "Abstract"])
        core, core_anchors = self._find_sentences(["propose", "we present", "we introduce", "our method", "approach"], ["Abstract", "Introduction", "Method"])
        method, method_anchors = self._section_text(["Method"], 7)
        experiments, experiment_anchors = self._section_text(["Experiments", "Results"], 6)
        limitations, limitation_anchors = self._find_sentences(["limitation", "future work", "fail", "cannot", "unable"], ["Limitations", "Discussion", "Conclusion"])
        claims = self._claims(max_items=6)
        return {
            "problem": {"summary": first_sentence(problem), "anchors": problem_anchors},
            "motivation": {"summary": first_sentence(motivation), "anchors": motivation_anchors},
            "core_idea": {"summary": first_sentence(core), "anchors": core_anchors},
            "method": {"summary": first_sentence(method), "anchors": method_anchors},
            "experiments": {"summary": first_sentence(experiments), "anchors": experiment_anchors},
            "claims": [{"claim_id": c["claim_id"], "claim": c["claim"], "anchors": c["anchors"]} for c in claims],
            "limitations": [
                {
                    "limitation": first_sentence(limitations) if limitations != "unknown" else "unknown",
                    "anchors": limitation_anchors,
                }
            ],
        }

    def _method_graph(self, skeleton: dict[str, Any]) -> dict[str, Any]:
        method_blocks = [b for b in self.by_section.get("Method", []) if b.type in {"paragraph", "formula"}]
        exp_blocks = [b for b in self.by_section.get("Experiments", []) + self.by_section.get("Results", []) if b.type == "paragraph"]
        abstract_blocks = [b for b in self.by_section.get("Abstract", []) if b.type == "paragraph"]
        nodes = [
            node("node_problem", "论文问题", "input", skeleton["problem"]["summary"], skeleton["problem"]["anchors"]),
            node("node_core", "核心思想", "module", skeleton["core_idea"]["summary"], skeleton["core_idea"]["anchors"]),
            node("node_method", "方法流程", "process", skeleton["method"]["summary"], skeleton["method"]["anchors"]),
            node("node_objective", "训练目标 / 推理过程", "objective", self._objective_summary(), self._objective_anchors()),
            node("node_output", "模型输出", "output", self._output_summary(), pick_anchors(method_blocks + abstract_blocks, 3)),
            node("node_eval", "实验评估", "evaluation", skeleton["experiments"]["summary"], skeleton["experiments"]["anchors"] or pick_anchors(exp_blocks, 3)),
        ]
        edges = [
            edge("node_problem", "node_core", "produces", "论文问题驱动核心方法设计。", skeleton["problem"]["anchors"] + skeleton["core_idea"]["anchors"]),
            edge("node_core", "node_method", "modifies", "核心思想被落实为具体模块或流程。", skeleton["core_idea"]["anchors"] + skeleton["method"]["anchors"]),
            edge("node_method", "node_objective", "optimizes", "方法通过目标函数、训练策略或推理流程产生效果。", skeleton["method"]["anchors"] + self._objective_anchors()),
            edge("node_objective", "node_output", "produces", "训练或推理过程产生输出。", self._objective_anchors() + pick_anchors(method_blocks, 1)),
            edge("node_output", "node_eval", "uses", "输出通过实验指标和数据集进行评估。", pick_anchors(method_blocks, 1) + skeleton["experiments"]["anchors"]),
        ]
        return {"nodes": nodes, "edges": edges}

    def _method_delta(self) -> dict[str, Any]:
        baseline_blocks = self._blocks_matching(["baseline", "previous", "existing", "prior", "compared with", "instead of"], ["Introduction", "Related Work", "Method"])
        new_blocks = self._blocks_matching(["propose", "we introduce", "we present", "our method", "new"], ["Abstract", "Introduction", "Method"])
        baseline_text = first_sentence(" ".join(b.content for b in baseline_blocks[:3])) if baseline_blocks else "unknown"
        new_text = first_sentence(" ".join(b.content for b in new_blocks[:3])) if new_blocks else self._skeleton()["core_idea"]["summary"]
        deltas = []
        delta_hints = [
            ("add", ["add", "augment", "introduce", "incorporate", "retrieve"]),
            ("replace", ["replace", "instead", "without", "remove"]),
            ("optimize", ["optimize", "objective", "loss", "preference"]),
            ("freeze", ["freeze", "frozen"]),
            ("rerank", ["rerank", "re-rank"]),
            ("prompt", ["prompt", "instruction"]),
            ("evaluate", ["benchmark", "evaluate", "metric"]),
        ]
        candidates = self._blocks_matching([h for _, hs in delta_hints for h in hs], ["Abstract", "Introduction", "Method"])
        for i, block in enumerate(candidates[:6], start=1):
            low = block.content.lower()
            change_type = next((kind for kind, hints in delta_hints if any(h in low for h in hints)), "replace")
            deltas.append(
                {
                    "delta_id": f"delta_{i}",
                    "component": infer_component(block.content),
                    "change_type": change_type,
                    "before": baseline_text,
                    "after": first_sentence(block.content),
                    "why_it_matters": "该变化可能对应论文声称的主要性能、效率或可用性改进；需结合证据链确认强度。",
                    "anchors": [block.anchor_id],
                }
            )
        if not deltas:
            anchor = pick_anchors(new_blocks or self.blocks, 1)
            deltas.append(
                {
                    "delta_id": "delta_1",
                    "component": "unknown",
                    "change_type": "replace",
                    "before": baseline_text,
                    "after": new_text,
                    "why_it_matters": "论文中未被启发式规则清晰识别；需要人工复核 baseline 与新方法差异。",
                    "anchors": anchor,
                }
            )
        return {
            "baseline_method": {"name": infer_name(baseline_text, "Baseline"), "description": baseline_text, "anchors": pick_anchors(baseline_blocks, 3)},
            "new_method": {"name": infer_name(new_text, "本文方法"), "description": new_text, "anchors": pick_anchors(new_blocks, 3)},
            "deltas": deltas,
        }

    def _formula_ir(self) -> dict[str, Any]:
        formula_blocks = [b for b in self.blocks if b.type == "formula"][:20]
        formulas = []
        for i, block in enumerate(formula_blocks, start=1):
            variables = []
            symbols = extract_symbols(block.content)
            context = self._neighbor_text(block)
            for symbol in symbols[:12]:
                confidence = "medium" if re.search(rf"\b{re.escape(symbol)}\b\s+(denotes|is|represents|为|表示)", context, re.I) else "low"
                variables.append(
                    {
                        "symbol": symbol,
                        "name": symbol,
                        "meaning": infer_variable_meaning(symbol, context),
                        "type": infer_variable_type(symbol, context),
                        "anchors": [block.anchor_id],
                        "confidence": confidence,
                    }
                )
            formulas.append(
                {
                    "formula_id": f"formula_{i}",
                    "latex": block.content,
                    "plain_language_summary": first_sentence(context) if context else "论文未明确定义该公式上下文。",
                    "role": infer_formula_role(block.content, context),
                    "variables": variables,
                    "dependencies": formula_dependencies(symbols),
                    "intuition": formula_intuition(block.content, context),
                    "anchors": [block.anchor_id],
                    "playground_config": {"enabled": False, "reason": "v1 预留互动公式组件，当前使用静态依赖图。"},
                }
            )
        return {"formulas": formulas}

    def _experiment_matrix(self) -> dict[str, Any]:
        exp_blocks = [
            b
            for b in self.blocks
            if (b.section in {"Experiments", "Results"} or b.type in {"caption", "table"})
            and b.type in {"paragraph", "caption"}
        ]
        experiments = []
        for i, block in enumerate(exp_blocks[:12], start=1):
            content = block.content
            experiments.append(
                {
                    "experiment_id": f"exp_{i}",
                    "name": infer_experiment_name(content, i),
                    "type": infer_experiment_type(content),
                    "dataset": infer_list(content, DATASET_HINTS),
                    "baseline": infer_baselines(content),
                    "metrics": infer_list(content, METRIC_HINTS),
                    "result_summary": first_sentence(content),
                    "what_it_tries_to_prove": infer_experiment_purpose(content),
                    "evidence_strength": infer_evidence_strength(content),
                    "anchors": [block.anchor_id],
                }
            )
        return {"experiments": experiments}

    def _claim_evidence(self, experiment_matrix: dict[str, Any]) -> dict[str, Any]:
        claims = self._claims(max_items=8)
        experiments = experiment_matrix.get("experiments", [])
        evidence_blocks = [b for b in self.blocks if b.section in {"Experiments", "Results"} or b.type in {"caption", "table"}]
        mapped = []
        for claim in claims:
            evidence = []
            for i, exp in enumerate(experiments[:3], start=1):
                support = "partially"
                if any(token in exp["result_summary"].lower() for token in ["outperform", "improve", "higher", "better", "achieve"]):
                    support = "strongly"
                evidence.append(
                    {
                        "evidence_id": f"{claim['claim_id']}_ev_{i}",
                        "source_type": "experiment",
                        "summary": exp["result_summary"],
                        "supports_claim": support,
                        "anchors": exp["anchors"],
                    }
                )
            if not evidence and evidence_blocks:
                block = evidence_blocks[0]
                evidence.append(
                    {
                        "evidence_id": f"{claim['claim_id']}_ev_1",
                        "source_type": source_type(block.type),
                        "summary": first_sentence(block.content),
                        "supports_claim": "weakly",
                        "anchors": [block.anchor_id],
                    }
                )
            flags = risk_flags_for_claim(claim["claim"], evidence)
            mapped.append(
                {
                    "claim_id": claim["claim_id"],
                    "claim": claim["claim"],
                    "claim_type": infer_claim_type(claim["claim"]),
                    "evidence": evidence,
                    "risk_flags": flags,
                    "overall_support": support_level(evidence, flags),
                }
            )
        return {"claims": mapped}

    def _glossary(self) -> dict[str, Any]:
        counter: Counter[str] = Counter()
        anchors: dict[str, list[str]] = {}
        for block in self.blocks:
            low = block.content.lower()
            for term in AI_TERMS:
                if term in low:
                    counter[term] += 1
                    anchors.setdefault(term, []).append(block.anchor_id)
        terms = []
        for term, count in counter.most_common(16):
            terms.append(
                {
                    "term": term,
                    "paper_specific_meaning": self._term_context(term),
                    "beginner_explanation": beginner_explanation(term),
                    "related_terms": related_terms(term),
                    "appears_in": anchors.get(term, [])[:5],
                    "importance": "high" if count >= 4 else "medium" if count >= 2 else "low",
                }
            )
        return {"terms": terms}

    def _reproduction(self) -> dict[str, Any]:
        all_text = " ".join(b.content for b in self.blocks)
        code_available = "yes" if re.search(r"\b(code|github|implementation)\b", all_text, re.I) else "unknown"
        datasets = infer_list(all_text, DATASET_HINTS)
        models = infer_list(all_text, MODEL_HINTS)
        compute = infer_compute(all_text)
        method_anchors = pick_anchors(self.by_section.get("Method", []), 3)
        exp_anchors = pick_anchors(self.by_section.get("Experiments", []) + self.by_section.get("Results", []), 3)
        steps = [
            {"step": "准备数据集", "description": "下载并整理论文使用的数据集；若数据集未明确列出，需人工从实验部分补全。", "anchors": exp_anchors},
            {"step": "准备基础模型 / 检索器 / 策略模型", "description": "根据方法部分配置模型、tokenizer、retriever 或 policy。", "anchors": method_anchors},
            {"step": "实现核心方法差异", "description": "优先复现 method delta 中列出的新增、替换或优化组件。", "anchors": method_anchors},
            {"step": "复现实验矩阵", "description": "按主实验、消融、鲁棒性和效率实验逐项复核指标。", "anchors": exp_anchors},
        ]
        missing = []
        if compute == "unknown":
            missing.append({"detail": "训练或评测算力未明确。", "why_it_matters": "算力差异会显著影响复现成本和结果稳定性。", "anchors": exp_anchors})
        if code_available == "unknown":
            missing.append({"detail": "未检测到明确代码链接。", "why_it_matters": "没有官方实现时，超参数和预处理细节更容易缺失。", "anchors": method_anchors})
        return {
            "reproduction": {
                "difficulty": "high" if compute == "unknown" or not datasets else "medium",
                "required_datasets": datasets or ["unknown"],
                "required_models": models or ["unknown"],
                "required_compute": compute,
                "code_available": code_available,
                "steps": steps,
                "missing_details": missing,
                "risk_points": [
                    {"risk": "parser 未能抽取 bbox。", "suggestion": "v1 使用 page + text_span 回跳；精确高亮需后续接 PyMuPDF bbox。"},
                    {"risk": "启发式 IR 可能漏掉隐含 baseline。", "suggestion": "在知微·辨中人工校正 delta，并绑定来源 anchor。"},
                ],
            }
        }

    def _find_sentences(self, keywords: list[str], sections: list[str]) -> tuple[str, list[str]]:
        candidates = self._blocks_matching(keywords, sections)
        if candidates:
            text = " ".join(first_sentence(b.content) for b in candidates[:3])
            return compact(text, 560), pick_anchors(candidates, 3)
        return "unknown", []

    def _blocks_matching(self, keywords: list[str], sections: list[str]) -> list[DocumentBlock]:
        section_set = set(sections)
        candidates = [b for b in self.blocks if (not section_set or b.section in section_set) and b.type in {"paragraph", "caption", "formula"}]
        result = []
        for block in candidates:
            low = block.content.lower()
            if any(keyword in low for keyword in keywords):
                result.append(block)
        return result

    def _claims(self, max_items: int = 6) -> list[dict[str, Any]]:
        claim_words = ["outperform", "improve", "achieve", "effective", "efficient", "robust", "generalize", "state-of-the-art", "better", "reduce"]
        sections = {"Abstract", "Introduction", "Results", "Conclusion"}
        candidates = []
        for block in self.blocks:
            if block.section not in sections or block.type != "paragraph":
                continue
            sentences = re.split(r"(?<=[.!?])\s+", block.content)
            for sentence in sentences:
                low = sentence.lower()
                if any(word in low for word in claim_words) and len(sentence) > 30:
                    candidates.append({"claim": compact(sentence, 300), "anchors": [block.anchor_id]})
        if not candidates:
            core, anchors = self._find_sentences(["propose", "present", "introduce"], ["Abstract", "Introduction"])
            candidates = [{"claim": core, "anchors": anchors}]
        return [
            {"claim_id": f"claim_{i}", "claim": item["claim"], "anchors": item["anchors"]}
            for i, item in enumerate(candidates[:max_items], start=1)
            if item["claim"] and item["claim"] != "unknown"
        ]

    def _objective_summary(self) -> str:
        blocks = self._blocks_matching(["loss", "objective", "optimize", "training", "inference"], ["Method"])
        if not blocks:
            blocks = [b for b in self.blocks if b.type == "formula"][:2]
        return first_sentence(" ".join(b.content for b in blocks[:2])) if blocks else "unknown"

    def _objective_anchors(self) -> list[str]:
        blocks = self._blocks_matching(["loss", "objective", "optimize", "training", "inference"], ["Method"])
        if not blocks:
            blocks = [b for b in self.blocks if b.type == "formula"][:2]
        return pick_anchors(blocks, 3)

    def _output_summary(self) -> str:
        blocks = self._blocks_matching(["output", "generate", "prediction", "answer", "label"], ["Abstract", "Method"])
        return first_sentence(" ".join(b.content for b in blocks[:2])) if blocks else "unknown"

    def _neighbor_text(self, target: DocumentBlock) -> str:
        idx = self.blocks.index(target)
        neighbors = self.blocks[max(0, idx - 2) : min(len(self.blocks), idx + 3)]
        return compact(" ".join(b.content for b in neighbors), 900)

    def _term_context(self, term: str) -> str:
        for block in self.blocks:
            if term in block.content.lower():
                return first_sentence(block.content, 260)
        return "unknown"


def source_type(block_type: str) -> str:
    return {
        "paragraph": "paragraph",
        "formula": "formula",
        "caption": "caption",
        "reference": "reference",
        "table": "table",
        "figure": "figure",
    }.get(block_type, "paragraph")


def pick_anchors(blocks: list[DocumentBlock], n: int = 3) -> list[str]:
    return [b.anchor_id for b in blocks[:n]]


def node(node_id: str, label: str, type_: str, description: str, anchors: list[str]) -> dict[str, Any]:
    return {"node_id": node_id, "label": label, "type": type_, "description": description or "unknown", "anchors": anchors}


def edge(from_: str, to: str, relation: str, description: str, anchors: list[str]) -> dict[str, Any]:
    return {"from": from_, "to": to, "relation": relation, "description": description, "anchors": dedupe(anchors)}


def dedupe(values: list[str]) -> list[str]:
    seen = set()
    out = []
    for value in values:
        if value and value not in seen:
            out.append(value)
            seen.add(value)
    return out


def infer_component(text: str) -> str:
    low = text.lower()
    for name in ["retriever", "reranker", "attention", "adapter", "objective", "loss", "policy", "reward model", "encoder", "decoder", "benchmark"]:
        if name in low:
            return name
    return "method component"


def infer_name(text: str, fallback: str) -> str:
    if not text or text == "unknown":
        return fallback
    words = re.findall(r"[A-Z][A-Za-z0-9\-]+", text)
    return " / ".join(words[:3]) if words else fallback


def extract_symbols(text: str) -> list[str]:
    raw = re.findall(r"(?<![A-Za-z])([A-Za-z][A-Za-z0-9_]{0,8})(?![A-Za-z])", text)
    stop = {"log", "min", "max", "arg", "exp", "sum", "softmax", "where", "for", "and", "the"}
    symbols = []
    for item in raw:
        if item.lower() not in stop and item not in symbols:
            symbols.append(item)
    return symbols


def infer_variable_meaning(symbol: str, context: str) -> str:
    patterns = [
        rf"{re.escape(symbol)}\s+(?:denotes|represents|is)\s+([^.;,]+)",
        rf"{re.escape(symbol)}\s*(?:为|表示)\s*([^。；，]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, context, re.I)
        if match:
            return compact(match.group(1), 120)
    return "论文未明确定义，系统根据公式上下文推测。"


def infer_variable_type(symbol: str, context: str) -> str:
    low = context.lower()
    if symbol.lower() in {"y", "label"} or "label" in low:
        return "label"
    if symbol.lower() in {"x", "input"} or "input" in low:
        return "input"
    if symbol.lower() in {"theta", "w", "b"} or "parameter" in low:
        return "parameter"
    if symbol.lower() in {"k", "n", "i", "j", "t"}:
        return "index"
    if "metric" in low or "score" in low:
        return "metric"
    return "latent"


def formula_dependencies(symbols: list[str]) -> list[dict[str, str]]:
    deps = []
    for left, right in zip(symbols[:6], symbols[1:7]):
        deps.append({"from": right, "to": left, "relation": "affects"})
    return deps


def infer_formula_role(formula: str, context: str) -> str:
    low = (formula + " " + context).lower()
    if "attention" in low or "softmax" in low:
        return "attention"
    if "loss" in low or "\\mathcal{l}" in low:
        return "loss"
    if "argmax" in low or "objective" in low or "optimize" in low:
        return "objective"
    if "prob" in low or "p(" in low:
        return "probability"
    if "metric" in low or "accuracy" in low or "f1" in low:
        return "metric"
    return "definition"


def formula_intuition(formula: str, context: str) -> str:
    role = infer_formula_role(formula, context)
    mapping = {
        "attention": "该公式描述信息如何被加权聚合；权重越高的输入对输出影响越大。",
        "loss": "该公式定义训练要最小化的误差或偏好代价。",
        "objective": "该公式定义模型优化方向，通常连接方法设计和实验效果。",
        "probability": "该公式把模型输出解释为概率或条件概率。",
        "metric": "该公式定义实验评价指标。",
    }
    return mapping.get(role, "该公式给出方法中的中间定义；变量含义需要结合上下文和原文锚点复核。")


DATASET_HINTS = ["ImageNet", "CIFAR", "MNIST", "HotpotQA", "Natural Questions", "SQuAD", "MS MARCO", "MMLU", "HELM", "BIG-bench", "COCO", "LAION", "WMT", "GSM8K", "HumanEval"]
METRIC_HINTS = ["accuracy", "F1", "EM", "BLEU", "ROUGE", "AUC", "perplexity", "win rate", "latency", "throughput", "cost", "recall", "precision"]
MODEL_HINTS = ["BERT", "T5", "GPT", "LLaMA", "Transformer", "CLIP", "ViT", "ResNet", "RoBERTa", "BART"]


def infer_list(text: str, hints: list[str]) -> list[str]:
    found = []
    low = text.lower()
    for hint in hints:
        if hint.lower() in low and hint not in found:
            found.append(hint)
    return found


def infer_baselines(text: str) -> list[str]:
    names = []
    for match in re.finditer(r"(?:baseline|compared with|against)\s+([A-Za-z0-9_\- /]+)", text, re.I):
        names.append(compact(match.group(1), 60))
    names += infer_list(text, ["BERT", "T5", "GPT", "Transformer", "BM25", "DPR", "LoRA", "RLHF", "DPO"])
    return dedupe(names)[:8]


def infer_experiment_name(text: str, i: int) -> str:
    if text.lower().startswith(("table", "figure", "fig.")):
        return compact(text, 80)
    return f"实验 {i}"


def infer_experiment_type(text: str) -> str:
    low = text.lower()
    if "ablation" in low:
        return "ablation"
    if "robust" in low:
        return "robustness"
    if "scaling" in low or "scale" in low:
        return "scaling"
    if "case study" in low or "example" in low:
        return "case_study"
    if "human" in low:
        return "human_eval"
    if "benchmark" in low:
        return "benchmark"
    if "efficien" in low or "latency" in low or "cost" in low:
        return "efficiency"
    return "main_result"


def infer_experiment_purpose(text: str) -> str:
    typ = infer_experiment_type(text)
    mapping = {
        "main_result": "证明整体方法相对 baseline 的主要效果。",
        "ablation": "验证某个模块或设计选择是否真的带来贡献。",
        "robustness": "验证方法在任务、数据或扰动变化下是否稳定。",
        "scaling": "验证规模变化对方法效果的影响。",
        "case_study": "提供直观例子，证据强度通常低于系统实验。",
        "human_eval": "通过人工评价补充自动指标。",
        "benchmark": "在标准评测集上定位方法表现。",
        "efficiency": "证明方法在速度、成本、参数量或算力上有优势。",
    }
    return mapping.get(typ, "unknown")


def infer_evidence_strength(text: str) -> str:
    low = text.lower()
    if "ablation" in low or "statistically" in low or "significant" in low:
        return "strong"
    if "case study" in low or "example" in low:
        return "weak"
    if any(word in low for word in ["table", "result", "benchmark", "evaluation"]):
        return "medium"
    return "unclear"


def infer_claim_type(text: str) -> str:
    low = text.lower()
    if "efficien" in low or "cost" in low or "latency" in low:
        return "efficiency"
    if "robust" in low:
        return "robustness"
    if "general" in low or "transfer" in low:
        return "generalization"
    if "interpret" in low:
        return "interpretability"
    if "safe" in low:
        return "safety"
    if "simple" in low:
        return "simplicity"
    return "performance"


def risk_flags_for_claim(claim: str, evidence: list[dict[str, Any]]) -> list[str]:
    flags = []
    if not evidence:
        flags.append("unsupported_claim")
    if evidence and all(ev["source_type"] == "case_study" or ev.get("supports_claim") == "weakly" for ev in evidence):
        flags.append("only_case_study")
    if not any("ablation" in ev.get("source_type", "") or "ablation" in ev.get("summary", "").lower() for ev in evidence):
        flags.append("no_ablation")
    if any(word in claim.lower() for word in ["state-of-the-art", "sota"]) and len(evidence) < 2:
        flags.append("unclear_baseline")
    return flags


def support_level(evidence: list[dict[str, Any]], flags: list[str]) -> str:
    if not evidence or "unsupported_claim" in flags:
        return "unsupported"
    if any(ev.get("supports_claim") == "strongly" for ev in evidence) and len(flags) <= 1:
        return "strong"
    if any(ev.get("supports_claim") in {"strongly", "partially"} for ev in evidence):
        return "medium"
    return "weak"


def beginner_explanation(term: str) -> str:
    mapping = {
        "attention": "让模型在多个输入片段中分配注意力权重的机制。",
        "transformer": "以 attention 为核心的神经网络结构，常用于语言和多模态模型。",
        "retrieval": "先从外部语料取回相关信息，再用于预测或生成。",
        "rag": "检索增强生成，把 retrieval 的上下文交给生成模型。",
        "lora": "只训练低秩增量矩阵的参数高效微调方法。",
        "adapter": "插入小模块进行微调，尽量少改动原模型。",
        "preference": "人类或模型给出的偏好对比信号。",
        "policy": "在强化学习或偏好优化中生成动作/文本的模型。",
        "reward": "衡量输出好坏的奖励信号。",
    }
    return mapping.get(term, "该术语在本文中需要结合出现位置理解；右侧来源可回跳原文。")


def related_terms(term: str) -> list[str]:
    groups = {
        "attention": ["transformer", "softmax", "encoder"],
        "retrieval": ["rag", "rerank", "embedding"],
        "rag": ["retrieval", "rerank", "generator"],
        "lora": ["adapter", "rank", "fine-tuning"],
        "preference": ["rlhf", "dpo", "reward"],
        "policy": ["reward", "rlhf", "optimization"],
    }
    return groups.get(term, [])


def infer_compute(text: str) -> str:
    match = re.search(r"((?:\d+\s*)?(?:A100|H100|V100|TPU|GPU|GPUs)[^.;]{0,80})", text, re.I)
    if match:
        return compact(match.group(1), 140)
    return "unknown"
