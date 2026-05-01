# @zhiwei/paper-ir

Open Paper IR schemas for 知微.

This package is the protocol boundary of the project. Parsers, extractors, renderers, benchmarks, and external tools should exchange paper understanding through these schemas rather than through UI-specific data.

## Schemas

- `schemas/paper-ir.schema.json`
- `schemas/source-anchor.schema.json`
- `schemas/formula-ir.schema.json`
- `schemas/claim-evidence.schema.json`
- `schemas/experiment-matrix.schema.json`
- `schemas/reproduction-roadmap.schema.json`

## Design Rule

Paper-specific generated content must carry source anchors.
