export const schemaVersion = "0.1.0";

export const sourceTypes = [
  "paragraph",
  "formula",
  "figure",
  "table",
  "caption",
  "reference"
];

export const moduleIds = [
  "structure",
  "formula",
  "evidence",
  "delta",
  "experiments",
  "reproduction"
];

export function anchorCount(ir) {
  return Array.isArray(ir?.anchors) ? ir.anchors.length : 0;
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

export function collectAnchorIds(value, result = new Set()) {
  if (!value) return result;
  if (Array.isArray(value)) {
    value.forEach((item) => collectAnchorIds(item, result));
    return result;
  }
  if (typeof value === "object") {
    if (Array.isArray(value.anchors)) value.anchors.forEach((id) => result.add(id));
    Object.values(value).forEach((item) => collectAnchorIds(item, result));
  }
  return result;
}
