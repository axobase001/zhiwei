# Claim-Evidence Specification

Claim-Evidence Map is the trust layer of 知微.

It answers:

> What exactly does the paper claim, and what evidence supports it?

## Claim Object

```json
{
  "claim_id": "claim_1",
  "claim": "The method improves translation quality over prior systems.",
  "claim_type": "performance",
  "evidence": [],
  "risk_flags": [],
  "overall_support": "strong"
}
```

## Evidence Object

```json
{
  "evidence_id": "ev_1",
  "source_type": "table",
  "summary": "Main result table reports BLEU improvements over baselines.",
  "supports_claim": "strongly",
  "anchors": ["anc_00110"]
}
```

## Risk Flags

- `unsupported_claim`
- `only_case_study`
- `no_ablation`
- `small_dataset`
- `unclear_baseline`
- `metric_mismatch`
- `missing_implementation_detail`

Renderers should surface risk flags near the claim, not bury them in export files.

## Schema

```text
packages/paper-ir/schemas/claim-evidence.schema.json
```
