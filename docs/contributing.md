# Contributing

知微 is organized as an open academic infrastructure project.

## Project Principles

- Paper IR first. UI must render structured data, not hardcoded paper content.
- Source grounding first. Generated paper-specific claims must cite anchors.
- Verification first. Missing anchors, unsupported claims, and low-confidence variables must remain visible.
- Examples are data. Demo papers belong in `examples/*/paper_ir.json`, not in UI components.
- Extensions should preserve the core schema and add fields instead of replacing the contract.

## Repository Layout

```text
apps/
  web/          Browser renderer and product shell
  api/          Vercel/serverless API adapter
  api-python/   Local Python API server
packages/
  paper-ir/     Open schema package
  parser/       PDF -> document blocks / source anchors
  extractor/    document blocks -> Paper IR
  renderer/     IR-driven rendering helpers
  benchmark/    benchmark and dataset generation tools
  playground/   experiments and local prototypes
examples/       example Paper IR files
docs/           public specs and project docs
```

## Adding A Paper Example

1. Put generated Paper IR at `examples/<paper-slug>/paper_ir.json`.
2. Ensure every module has anchors.
3. Run grounding verification.
4. Add a short README explaining source and generation mode.

## Adding A Schema Field

1. Prefer optional fields first.
2. Update `packages/paper-ir/schemas/*`.
3. Update docs.
4. Update renderer behavior if the field affects UI.
5. Add or update an example Paper IR.
