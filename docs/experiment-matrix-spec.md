# Experiment Matrix Specification

Experiment Matrix explains what each experiment is trying to prove.

It is not a table extractor. Tables, figures, paragraphs, and captions can all become evidence, but the matrix item should express the experiment logic.

```json
{
  "experiment_id": "experiment_1",
  "name": "Main result on WMT 2014 En-De",
  "type": "main_result",
  "dataset": ["WMT 2014 En-De"],
  "baseline": ["RNN encoder-decoder", "CNN sequence model"],
  "metrics": ["BLEU"],
  "result_summary": "The model reports stronger BLEU than prior systems.",
  "what_it_tries_to_prove": "The overall method improves translation quality.",
  "evidence_strength": "strong",
  "anchors": ["anc_00110"]
}
```

## Types

- `main_result`
- `ablation`
- `robustness`
- `scaling`
- `case_study`
- `human_eval`
- `benchmark`
- `efficiency`

## Schema

```text
packages/paper-ir/schemas/experiment-matrix.schema.json
```
