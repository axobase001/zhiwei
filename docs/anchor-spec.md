# Source Anchor Specification

Source Anchor is the grounding unit of 知微.

It connects generated Paper IR nodes back to the original paper location.

```json
{
  "anchor_id": "anc_00042",
  "page": 3,
  "section": "Method",
  "bbox": {
    "x": 72,
    "y": 140,
    "width": 420,
    "height": 58
  },
  "text_span": "The model computes attention weights ...",
  "source_type": "paragraph"
}
```

## Required Fields

- `anchor_id`: stable identifier used by all Paper IR modules.
- `page`: 1-based PDF page number.
- `text_span`: original text excerpt.
- `source_type`: one of `paragraph`, `formula`, `figure`, `table`, `caption`, `reference`.

## Optional Fields

- `section`: parser-detected or classifier-detected section.
- `bbox`: reserved for PDF highlighting. If exact geometry is unavailable, keep it `null`.

## Renderer Expectations

- Clicking an anchor should navigate to the source page.
- If `bbox` exists, renderer should highlight the box.
- If only `page + text_span` exists, renderer should show the source excerpt and page jump.

## Schema

```text
packages/paper-ir/schemas/source-anchor.schema.json
```
