# @zhiwei/parser

Parser package for converting PDFs into normalized document blocks and source anchors.

The parser contract is:

```json
{
  "block_id": "string",
  "type": "title | abstract | section_heading | paragraph | formula | figure | table | caption | reference",
  "content": "string",
  "page": 1,
  "section": "Method",
  "bbox": null,
  "anchor_id": "anc_00001"
}
```

Downstream packages must not depend on private parser output formats. Any parser adapter must normalize into this block contract first.
