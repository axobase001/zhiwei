# @zhiwei/benchmark

Benchmark tooling for generating and evaluating Paper IR examples.

Current Python scripts:

- `python/benchmark_pipeline.py`: run the Mimo/OpenAI-compatible Paper IR pipeline for configured benchmark papers.
- `python/semantic_ml_pipeline.py`: fetch high-citation ML candidates from Semantic Scholar and run the same pipeline.

The benchmark package should only orchestrate:

- PDF download,
- parsing,
- source anchor generation,
- extractor calls,
- grounding verification,
- quality reports.

It should not hand-author paper analysis content.
