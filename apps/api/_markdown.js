function list(value) {
  return Array.isArray(value) && value.length ? value.join(", ") : "unknown";
}

function toMarkdown(ir) {
  const meta = ir.metadata || {};
  const skeleton = ir.paper_skeleton || {};
  const delta = ir.method_delta || {};
  const lines = [
    `# ${meta.title || "未命名论文"} - 知微结构化笔记`,
    "",
    `- 生成时间：${ir.generated_at || "unknown"}`,
    `- 论文范围：${(ir.scope || {}).supported_domain || "unknown"}`,
    "",
    "## 论文骨架"
  ];

  for (const [key, label] of [
    ["problem", "问题"],
    ["motivation", "动机"],
    ["core_idea", "核心思想"],
    ["method", "方法"],
    ["experiments", "实验"]
  ]) {
    const item = skeleton[key] || {};
    lines.push(`### ${label}`, item.summary || "unknown", `来源：${list(item.anchors)}`, "");
  }

  lines.push("## 方法差异");
  lines.push(`- Baseline：${(delta.baseline_method || {}).description || "unknown"}`);
  lines.push(`- New Method：${(delta.new_method || {}).description || "unknown"}`, "");
  for (const item of delta.deltas || []) {
    lines.push(`### ${item.component || "unknown"} (${item.change_type || "unknown"})`);
    lines.push(`- Before：${item.before || "unknown"}`);
    lines.push(`- After：${item.after || "unknown"}`);
    lines.push(`- Why：${item.why_it_matters || "unknown"}`);
    lines.push(`- 来源：${list(item.anchors)}`, "");
  }

  lines.push("## 公式拆解");
  for (const formula of ((ir.formula_ir || {}).formulas || [])) {
    lines.push(`### ${formula.formula_id} - ${formula.role}`);
    lines.push("```latex", formula.latex || "", "```");
    lines.push(formula.intuition || "", `来源：${list(formula.anchors)}`, "");
  }

  lines.push("## 证据链");
  for (const claim of (((ir.claim_evidence_map || {}).claims) || [])) {
    lines.push(`### ${claim.claim_id}：${claim.claim}`);
    lines.push(`- 类型：${claim.claim_type}`);
    lines.push(`- 支持强度：${claim.overall_support}`);
    lines.push(`- 风险：${list(claim.risk_flags)}`);
    for (const ev of claim.evidence || []) {
      lines.push(`- Evidence：${ev.summary}；支持：${ev.supports_claim}；来源：${list(ev.anchors)}`);
    }
    lines.push("");
  }

  lines.push("## 实验逻辑");
  for (const exp of (((ir.experiment_matrix || {}).experiments) || [])) {
    lines.push(`### ${exp.name}`);
    lines.push(`- 类型：${exp.type}`);
    lines.push(`- 数据集：${list(exp.dataset)}`);
    lines.push(`- Baseline：${list(exp.baseline)}`);
    lines.push(`- 指标：${list(exp.metrics)}`);
    lines.push(`- 想证明：${exp.what_it_tries_to_prove}`);
    lines.push(`- 结果：${exp.result_summary}`);
    lines.push(`- 来源：${list(exp.anchors)}`, "");
  }

  return lines.join("\n");
}

module.exports = { toMarkdown };
