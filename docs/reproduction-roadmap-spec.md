# Reproduction Roadmap Specification

Reproduction Roadmap describes how a reader could attempt to reproduce the paper and where the paper leaves uncertainty.

It must not invent missing implementation details.

```json
{
  "reproduction": {
    "difficulty": "medium",
    "required_datasets": ["WMT 2014 En-De"],
    "required_models": ["Transformer base"],
    "required_compute": "unknown",
    "code_available": "unknown",
    "steps": [
      {
        "step": "Prepare dataset",
        "description": "Download and preprocess the machine translation dataset.",
        "anchors": ["anc_00102"]
      }
    ],
    "missing_details": [
      {
        "detail": "Exact preprocessing script is not specified.",
        "why_it_matters": "Different tokenization can change evaluation scores.",
        "anchors": ["anc_00102"]
      }
    ],
    "risk_points": [
      {
        "risk": "BLEU reproduction may differ due to preprocessing.",
        "suggestion": "Record tokenizer and evaluation settings."
      }
    ]
  }
}
```

## Schema

```text
packages/paper-ir/schemas/reproduction-roadmap.schema.json
```
