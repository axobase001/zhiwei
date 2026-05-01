# Formula IR Specification

Formula IR represents important formulas as inspectable objects rather than inert LaTeX.

Each formula must preserve:

- original or reconstructed LaTeX,
- formula role,
- variables,
- variable confidence,
- dependencies,
- intuition,
- source anchors.

## Example

```json
{
  "formula_id": "formula_attention",
  "latex": "Attention(Q,K,V)=softmax(QK^T / sqrt(d_k))V",
  "role": "attention",
  "variables": [
    {
      "symbol": "Q",
      "name": "Query",
      "meaning": "current position asks what information to retrieve",
      "type": "input",
      "anchors": ["anc_00012"],
      "confidence": "high"
    }
  ],
  "dependencies": [
    { "from": "Q", "to": "K", "relation": "compares_with" }
  ],
  "intuition": "Dot products compare tokens, softmax turns scores into weights, and V is aggregated.",
  "anchors": ["anc_00012"]
}
```

## Confidence

- `high`: explicitly defined by the paper.
- `medium`: inferred from local context.
- `low`: uncertain or underdefined. UI must expose the uncertainty.

Unknown variables must not be presented as facts.

## Schema

```text
packages/paper-ir/schemas/formula-ir.schema.json
```
