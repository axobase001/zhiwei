from __future__ import annotations

from typing import Any


def ir_to_markdown(ir: dict[str, Any]) -> str:
    meta = ir.get("metadata", {})
    lines = [
        f"# {meta.get('title', '未命名论文')} - 知微结构化笔记",
        "",
        f"- 生成时间：{ir.get('generated_at', 'unknown')}",
        f"- 论文范围：{ir.get('scope', {}).get('supported_domain', 'unknown')}",
        "",
        "## 论文骨架",
    ]
    skeleton = ir.get("paper_skeleton", {})
    for key, label in [
        ("problem", "问题"),
        ("motivation", "动机"),
        ("core_idea", "核心思想"),
        ("method", "方法"),
        ("experiments", "实验"),
    ]:
        item = skeleton.get(key, {})
        lines += [f"### {label}", item.get("summary", "unknown"), f"来源：{', '.join(item.get('anchors', []))}", ""]

    lines += ["## 方法差异"]
    delta = ir.get("method_delta", {})
    lines += [
        f"- Baseline：{delta.get('baseline_method', {}).get('description', 'unknown')}",
        f"- New Method：{delta.get('new_method', {}).get('description', 'unknown')}",
        "",
    ]
    for item in delta.get("deltas", []):
        lines += [
            f"### {item.get('component', 'unknown')} ({item.get('change_type', 'unknown')})",
            f"- Before：{item.get('before', 'unknown')}",
            f"- After：{item.get('after', 'unknown')}",
            f"- Why：{item.get('why_it_matters', 'unknown')}",
            f"- 来源：{', '.join(item.get('anchors', []))}",
            "",
        ]

    lines += ["## 公式拆解"]
    for formula in ir.get("formula_ir", {}).get("formulas", []):
        lines += [
            f"### {formula.get('formula_id')} - {formula.get('role', 'definition')}",
            f"```latex\n{formula.get('latex', '')}\n```",
            formula.get("intuition", ""),
            f"来源：{', '.join(formula.get('anchors', []))}",
            "",
        ]
        for variable in formula.get("variables", []):
            lines.append(f"- `{variable.get('symbol')}`：{variable.get('meaning')}（confidence={variable.get('confidence')}）")
        lines.append("")

    lines += ["## 证据链"]
    for claim in ir.get("claim_evidence_map", {}).get("claims", []):
        lines += [
            f"### {claim.get('claim_id')}：{claim.get('claim')}",
            f"- 类型：{claim.get('claim_type')}",
            f"- 支持强度：{claim.get('overall_support')}",
            f"- 风险：{', '.join(claim.get('risk_flags', [])) or '无'}",
        ]
        for ev in claim.get("evidence", []):
            lines.append(f"- Evidence：{ev.get('summary')}；支持：{ev.get('supports_claim')}；来源：{', '.join(ev.get('anchors', []))}")
        lines.append("")

    lines += ["## 实验逻辑"]
    for exp in ir.get("experiment_matrix", {}).get("experiments", []):
        lines += [
            f"### {exp.get('name')}",
            f"- 类型：{exp.get('type')}",
            f"- 数据集：{', '.join(exp.get('dataset', [])) or 'unknown'}",
            f"- Baseline：{', '.join(exp.get('baseline', [])) or 'unknown'}",
            f"- 指标：{', '.join(exp.get('metrics', [])) or 'unknown'}",
            f"- 想证明：{exp.get('what_it_tries_to_prove')}",
            f"- 结果：{exp.get('result_summary')}",
            f"- 来源：{', '.join(exp.get('anchors', []))}",
            "",
        ]

    reproduction = ir.get("reproduction_roadmap", {}).get("reproduction", {})
    lines += [
        "## 复现路线",
        f"- 难度：{reproduction.get('difficulty', 'unknown')}",
        f"- 数据集：{', '.join(reproduction.get('required_datasets', []))}",
        f"- 模型：{', '.join(reproduction.get('required_models', []))}",
        f"- 算力：{reproduction.get('required_compute', 'unknown')}",
        f"- 代码可用：{reproduction.get('code_available', 'unknown')}",
        "",
    ]
    for step in reproduction.get("steps", []):
        lines.append(f"- {step.get('step')}：{step.get('description')} 来源：{', '.join(step.get('anchors', []))}")
    lines.append("")

    verification = ir.get("verification", {})
    lines += ["## Grounding Verification"]
    for warning in verification.get("warnings", []):
        lines.append(f"- [{warning.get('severity')}] {warning.get('code')}：{warning.get('message')}")
    return "\n".join(lines)
