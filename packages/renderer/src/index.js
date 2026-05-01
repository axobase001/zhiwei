export function paperTitle(ir) {
  return ir?.metadata?.title || "未命名论文";
}

export function paperSubtitle(ir) {
  return ir?.paper_skeleton?.core_idea?.summary || ir?.paper_skeleton?.method?.summary || "";
}

export function anchorsById(ir) {
  return new Map((ir?.anchors || []).map((anchor) => [anchor.anchor_id, anchor]));
}

export function graphNodes(ir) {
  return (ir?.method_graph?.nodes || []).map((node) => ({
    id: node.node_id || node.id,
    title: node.title || node.label || node.node_id,
    summary: node.summary || node.description || "",
    type: node.type || "module",
    anchors: node.anchors || [],
    raw: node
  }));
}

export function moduleCounts(ir) {
  return {
    structure: ir?.method_graph?.nodes?.length || 0,
    formula: ir?.formula_ir?.formulas?.length || 0,
    evidence: ir?.claim_evidence_map?.claims?.length || 0,
    delta: ir?.method_delta?.deltas?.length || 0,
    experiments: ir?.experiment_matrix?.experiments?.length || 0,
    reproduction: ir?.reproduction_roadmap?.reproduction?.steps?.length || 0
  };
}
