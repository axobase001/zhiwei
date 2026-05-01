# @zhiwei/extractor

Extractor package for compiling document blocks into Paper IR.

Extractor implementations may be:

- heuristic,
- LLM-based,
- hybrid multi-pass,
- human-corrected.

All implementations must preserve the same output contract:

- strict Paper IR JSON,
- source anchors on paper-specific statements,
- confidence labels for inferred formula variables,
- claim-evidence links,
- verification warnings instead of silent success.
