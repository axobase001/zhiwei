# Roadmap

## Stage 1: AI / LLM / ML Method Papers

- Paper IR schema package.
- Source Anchor schema.
- Formula IR.
- Claim-Evidence Map.
- Experiment Matrix.
- Reproduction Roadmap.
- IR-driven web renderer.
- Benchmark examples for canonical AI / LLM / ML papers.

## Stage 2: Parser Quality

- Improve PDF layout parsing and bbox fidelity.
- Add parser adapters for PyMuPDF, GROBID, Marker, and Nougat-style outputs.
- Normalize all parser outputs into document blocks and anchors.
- Add regression tests for anchor stability.

## Stage 3: Extraction Quality

- Multi-pass LLM extraction.
- Schema-constrained repair.
- Grounding verification scoring.
- Gold benchmark comparison.
- Unsupported-claim detection.

## Stage 4: Renderer Components

- Framework-agnostic graph renderer.
- Formula renderer and variable dependency view.
- Claim-evidence view.
- Experiment matrix view.
- PDF anchor navigation.

## Stage 5: Broader Research Infrastructure

- More domains only after AI / LLM / ML method papers are stable.
- Community-maintained paper benchmarks.
- Interoperability with citation graphs and literature databases.
- Export formats for notes, datasets, and downstream analysis.
