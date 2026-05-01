from __future__ import annotations

from typing import Any


def verify_ir(ir: dict[str, Any]) -> dict[str, Any]:
    anchors = {a["anchor_id"] for a in ir.get("anchors", [])}
    warnings: list[dict[str, Any]] = []

    def warn(code: str, message: str, target: str | None = None, severity: str = "medium") -> None:
        warnings.append({"code": code, "message": message, "target": target, "severity": severity})

    def check_anchor_list(values: Any, target: str, required: bool = True) -> None:
        if not isinstance(values, list) or not values:
            if required:
                warn("missing_anchor", "生成节点缺少 source anchor。", target, "high")
            return
        missing = [value for value in values if value not in anchors]
        if missing:
            warn("unknown_anchor", f"引用了不存在的 anchor: {', '.join(missing[:5])}", target, "high")

    skeleton = ir.get("paper_skeleton", {})
    for key in ["problem", "motivation", "core_idea", "method", "experiments"]:
        check_anchor_list(skeleton.get(key, {}).get("anchors"), f"paper_skeleton.{key}", required=key in {"problem", "method"})
    for item in skeleton.get("claims", []):
        check_anchor_list(item.get("anchors"), f"paper_skeleton.claims.{item.get('claim_id')}")

    for node in ir.get("method_graph", {}).get("nodes", []):
        check_anchor_list(node.get("anchors"), f"method_graph.nodes.{node.get('node_id')}")
    for edge in ir.get("method_graph", {}).get("edges", []):
        check_anchor_list(edge.get("anchors"), f"method_graph.edges.{edge.get('from')}->{edge.get('to')}", required=False)

    for delta in ir.get("method_delta", {}).get("deltas", []):
        check_anchor_list(delta.get("anchors"), f"method_delta.{delta.get('delta_id')}")

    for formula in ir.get("formula_ir", {}).get("formulas", []):
        check_anchor_list(formula.get("anchors"), f"formula_ir.{formula.get('formula_id')}")
        for variable in formula.get("variables", []):
            if variable.get("confidence") not in {"high", "medium", "low"}:
                warn("missing_confidence", "公式变量缺少 confidence。", f"{formula.get('formula_id')}.{variable.get('symbol')}", "high")
            check_anchor_list(variable.get("anchors"), f"{formula.get('formula_id')}.{variable.get('symbol')}", required=False)

    for exp in ir.get("experiment_matrix", {}).get("experiments", []):
        check_anchor_list(exp.get("anchors"), f"experiment_matrix.{exp.get('experiment_id')}")
        if not exp.get("what_it_tries_to_prove"):
            warn("missing_experiment_logic", "实验缺少证明意图说明。", exp.get("experiment_id"), "medium")

    for claim in ir.get("claim_evidence_map", {}).get("claims", []):
        evidence = claim.get("evidence") or []
        if not evidence:
            warn("claim_without_evidence", "claim 没有关联 evidence。", claim.get("claim_id"), "high")
        for ev in evidence:
            check_anchor_list(ev.get("anchors"), f"claim_evidence.{claim.get('claim_id')}.{ev.get('evidence_id')}")
        if claim.get("overall_support") in {"strong", "medium"} and any(flag == "unsupported_claim" for flag in claim.get("risk_flags", [])):
            warn("support_conflict", "claim 同时被标为有支持和 unsupported。", claim.get("claim_id"), "high")

    for step in ir.get("reproduction_roadmap", {}).get("reproduction", {}).get("steps", []):
        check_anchor_list(step.get("anchors"), f"reproduction.{step.get('step')}", required=False)

    if not warnings:
        warnings.append({"code": "ok", "message": "Grounding verification passed with current v1 checks.", "target": None, "severity": "info"})

    return {
        "status": "passed" if all(w["severity"] in {"info", "low"} for w in warnings) else "warning",
        "warnings": warnings,
        "anchor_count": len(anchors),
    }
