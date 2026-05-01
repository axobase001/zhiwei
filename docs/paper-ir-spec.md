# Paper IR Specification

Paper IR is the open intermediate representation used by 知微 to compile a static paper PDF into an interactive, traceable, and verifiable knowledge interface.

The core rule is simple:

> Every generated explanation node must cite source anchors.

Paper IR is not a summary format. It is a structured contract between parser, extractor, verifier, renderer, benchmark, and user correction layers.

## Top-Level Object

```json
{
  "schema_version": "0.1.0",
  "metadata": {},
  "anchors": [],
  "paper_skeleton": {},
  "method_graph": {},
  "method_delta": {},
  "formula_ir": {},
  "experiment_matrix": {},
  "claim_evidence_map": {},
  "glossary": {},
  "reproduction_roadmap": {},
  "verification": {}
}
```

## Required Modules

- `paper_skeleton`: problem, motivation, core idea, method, experiments, claims, limitations.
- `method_graph`: typed nodes and edges for structure rendering.
- `method_delta`: baseline, new method, and concrete changes.
- `formula_ir`: formulas, variables, dependencies, confidence, intuition.
- `experiment_matrix`: experiments grouped by proof intent.
- `claim_evidence_map`: claims linked to evidence and risk flags.
- `glossary`: paper-specific term meanings.
- `reproduction_roadmap`: datasets, models, compute, steps, missing details, risks.

## Grounding

Every object that makes a paper-specific statement must include `anchors: ["anchor_id"]`.

Renderers must treat missing anchors as a warning state, not as a normal successful result.

## Schema

Canonical JSON Schema lives in:

```text
packages/paper-ir/schemas/paper-ir.schema.json
```

The schema is intentionally permissive with `additionalProperties: true` so downstream research prototypes can extend it without forking the core protocol.
