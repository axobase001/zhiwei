from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, PROJECT_ROOT
from .llm import OpenAICompatibleProvider
from .parser import DocumentBlock, parse_pdf
from .utils import compact, json_dumps, now_iso
from .verifier import verify_ir


PAPERS = [
    {
        "paper_id": "paper_attention_2017",
        "title": "Attention Is All You Need",
        "authors": ["Ashish Vaswani et al."],
        "year": 2017,
        "venue": "NeurIPS",
        "arxiv_id": "1706.03762",
        "paper_type": "Transformer / Attention architecture paper",
        "pdf_url": "https://arxiv.org/pdf/1706.03762",
    },
    {
        "paper_id": "paper_lora_2021",
        "title": "LoRA: Low-Rank Adaptation of Large Language Models",
        "authors": ["Edward J. Hu et al."],
        "year": 2021,
        "venue": "arXiv / ICLR",
        "arxiv_id": "2106.09685",
        "paper_type": "PEFT / LoRA method paper",
        "pdf_url": "https://arxiv.org/pdf/2106.09685",
    },
    {
        "paper_id": "paper_rag_2020",
        "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
        "authors": ["Patrick Lewis et al."],
        "year": 2020,
        "venue": "NeurIPS",
        "arxiv_id": "2005.11401",
        "paper_type": "RAG / Retrieval / Generation",
        "pdf_url": "https://arxiv.org/pdf/2005.11401",
    },
    {
        "paper_id": "paper_dpo_2023",
        "title": "Direct Preference Optimization: Your Language Model is Secretly a Reward Model",
        "authors": ["Rafael Rafailov et al."],
        "year": 2023,
        "venue": "NeurIPS",
        "arxiv_id": "2305.18290",
        "paper_type": "Preference Optimization / DPO / Alignment",
        "pdf_url": "https://arxiv.org/pdf/2305.18290",
    },
    {
        "paper_id": "paper_instructgpt_2022",
        "title": "Training language models to follow instructions with human feedback",
        "authors": ["Long Ouyang et al."],
        "year": 2022,
        "venue": "NeurIPS",
        "arxiv_id": "2203.02155",
        "paper_type": "RLHF / Instruction Following / Alignment",
        "pdf_url": "https://arxiv.org/pdf/2203.02155",
    },
    {
        "paper_id": "paper_bert_2018",
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "authors": ["Jacob Devlin et al."],
        "year": 2018,
        "venue": "NAACL",
        "arxiv_id": "1810.04805",
        "paper_type": "Pre-training / Bidirectional Transformer / BERT",
        "pdf_url": "https://arxiv.org/pdf/1810.04805",
    },
    {
        "paper_id": "paper_react_2022",
        "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
        "authors": ["Shunyu Yao et al."],
        "year": 2022,
        "venue": "ICLR",
        "arxiv_id": "2210.03629",
        "paper_type": "Agent / Tool-use / Reasoning and Acting",
        "pdf_url": "https://arxiv.org/pdf/2210.03629",
    },
    {
        "paper_id": "paper_clip_2021",
        "title": "CLIP: Learning Transferable Visual Models From Natural Language Supervision",
        "authors": ["Alec Radford et al."],
        "year": 2021,
        "venue": "ICML",
        "arxiv_id": "2103.00020",
        "paper_type": "Multimodal / Contrastive Learning / Vision-Language",
        "pdf_url": "https://arxiv.org/pdf/2103.00020",
    },
]


OUT_DIR = PROJECT_ROOT / "samples" / "benchmark" / "generated"
PDF_DIR = PROJECT_ROOT / "data" / "benchmark_pdfs"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run Zhiwei benchmark Paper IR pipeline with Mimo/OpenAI-compatible API.")
    parser.add_argument("--paper", action="append", help="Run only selected paper_id. Can be repeated.")
    parser.add_argument("--spec-file", help="JSON file containing additional or replacement paper specs.")
    parser.add_argument("--force", action="store_true", help="Regenerate existing IR files.")
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--sleep", type=float, default=1.0, help="Sleep seconds between API calls.")
    args = parser.parse_args(argv)

    ensure_api_config()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    specs = load_specs(args.spec_file) if args.spec_file else PAPERS
    selected = [p for p in specs if not args.paper or p["paper_id"] in set(args.paper)]
    provider = OpenAICompatibleProvider(LLM_BASE_URL, LLM_API_KEY, LLM_MODEL)
    summary = []
    summary_stem = Path(args.spec_file).stem if args.spec_file else "benchmark"
    summary_path = OUT_DIR / f"{summary_stem}_summary.json"
    for index, spec in enumerate(selected, start=1):
        print(f"[{index}/{len(selected)}] {spec['paper_id']} :: {spec['title']}", flush=True)
        try:
            result = run_one(spec, provider, force=args.force, skip_download=args.skip_download)
            summary.append(result)
            print(f"  ok anchors={result['anchor_count']} formulas={result['formula_count']} warnings={result['warning_count']}", flush=True)
        except Exception as exc:
            item = {"paper_id": spec["paper_id"], "title": spec["title"], "status": "failed", "error": str(exc)}
            summary.append(item)
            print(f"  failed: {exc}", flush=True)
        summary_path.write_text(json.dumps({"generated_at": now_iso(), "model": LLM_MODEL, "papers": summary}, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(args.sleep)

    summary_path.write_text(json.dumps({"generated_at": now_iso(), "model": LLM_MODEL, "papers": summary}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"summary: {summary_path}", flush=True)
    return 0 if all(item.get("status") == "ok" for item in summary) else 1


def ensure_api_config() -> None:
    missing = []
    if not LLM_BASE_URL:
        missing.append("OPENAI_BASE_URL / ZHIWEI_LLM_BASE_URL")
    if not LLM_MODEL:
        missing.append("OPENAI_MODEL / ZHIWEI_LLM_MODEL")
    if not LLM_API_KEY:
        missing.append("OPENAI_API_KEY / ZHIWEI_LLM_API_KEY")
    if missing:
        raise RuntimeError("Missing Mimo/OpenAI-compatible API config: " + ", ".join(missing))


def load_specs(spec_file: str) -> list[dict[str, Any]]:
    path = Path(spec_file)
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        for key in ["papers", "selected", "specs"]:
            if isinstance(data.get(key), list):
                data = data[key]
                break
    if not isinstance(data, list):
        raise RuntimeError(f"Spec file must contain a list of paper specs: {path}")
    return [item for item in data if isinstance(item, dict)]


def enrich_metadata(metadata: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    for key in [
        "citation_count",
        "influential_citation_count",
        "semantic_scholar_id",
        "semantic_scholar_url",
        "importance_rank",
        "selection_source",
        "open_access_pdf_url",
        "fields_of_study",
        "publication_types",
        "abstract",
    ]:
        if spec.get(key) is not None:
            metadata[key] = spec[key]
    return metadata


def run_one(spec: dict[str, Any], provider: OpenAICompatibleProvider, force: bool, skip_download: bool) -> dict[str, Any]:
    paper_dir = OUT_DIR / spec["paper_id"]
    paper_dir.mkdir(parents=True, exist_ok=True)
    ir_path = paper_dir / "paper_ir.json"
    if ir_path.exists() and not force:
        ir = json.loads(ir_path.read_text(encoding="utf-8"))
        anchors_path = paper_dir / "anchors.json"
        existing_anchors = json.loads(anchors_path.read_text(encoding="utf-8")) if anchors_path.exists() else ir.get("anchors", [])
        existing_metadata = ir.get("metadata") or {
            "paper_id": spec["paper_id"],
            "title": spec["title"],
            "authors": spec["authors"],
            "venue": spec["venue"],
            "year": spec["year"],
            "arxiv_id": spec["arxiv_id"],
            "doi": None,
            "uploaded_at": now_iso(),
            "language": "en",
            "paper_type": spec["paper_type"],
        }
        enrich_metadata(existing_metadata, spec)
        ir = normalize_ir(ir, existing_metadata, existing_anchors)
        ir["verification"] = verify_ir(ir)
        report = quality_report(ir)
        ir_path.write_text(json.dumps(ir, ensure_ascii=False, indent=2), encoding="utf-8")
        report_path = paper_dir / "quality_report.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return report | {"status": "ok", "paper_id": spec["paper_id"], "title": spec["title"], "cached": True}

    pdf_path = PDF_DIR / f"{spec['paper_id']}.pdf"
    download_error = ""
    if skip_download and not pdf_path.exists():
        metadata, blocks = metadata_fallback_document(spec, "PDF download skipped and no local PDF exists.")
    else:
        if not skip_download and (not pdf_path.exists() or force):
            try:
                download_pdf_candidates(pdf_url_candidates(spec), pdf_path)
            except Exception as exc:
                download_error = str(exc)
        if pdf_path.exists():
            metadata, blocks = parse_pdf(pdf_path, spec["paper_id"])
            metadata["source_mode"] = "pdf"
        else:
            metadata, blocks = metadata_fallback_document(spec, download_error or "PDF is unavailable.")
    metadata.update(
        {
            "paper_id": spec["paper_id"],
            "title": spec["title"],
            "authors": spec["authors"],
            "venue": spec["venue"],
            "year": spec["year"],
            "arxiv_id": spec["arxiv_id"],
            "doi": metadata.get("doi"),
            "uploaded_at": now_iso(),
            "language": "en",
            "paper_type": spec["paper_type"],
        }
    )
    if download_error:
        metadata["pdf_download_error"] = download_error
    enrich_metadata(metadata, spec)
    anchors = anchors_from_blocks(blocks)

    blocks_path = paper_dir / "document_blocks.json"
    anchors_path = paper_dir / "anchors.json"
    blocks_path.write_text(json.dumps([block_to_json(b) for b in blocks], ensure_ascii=False, indent=2), encoding="utf-8")
    anchors_path.write_text(json.dumps(anchors, ensure_ascii=False, indent=2), encoding="utf-8")

    selected_blocks = select_context_blocks(blocks)
    prompt_payload = {
        "paper_metadata": metadata,
        "source_anchor_rules": [
            "Every generated explanation, node, formula, claim, experiment, delta, glossary term and reproduction step must cite anchor_id values from provided document_blocks.",
            "Do not invent anchor_id values.",
            "If a variable or implementation detail is inferred rather than explicitly defined, set confidence to medium or low.",
            "Unknown details must be written as unknown or missing_details, not fabricated.",
            "If paper_metadata.source_mode is metadata_abstract_fallback, only use the provided metadata and abstract. Mark unavailable formulas, tables, figures, experiments, and implementation details as unknown or missing_details rather than inventing them.",
        ],
        "document_blocks": [block_prompt_json(b) for b in selected_blocks],
        "required_modules": ["知微·构", "知微·析", "知微·证", "知微·辨", "知微·验", "知微·径"],
    }
    ir = call_mimo_for_ir(provider, prompt_payload)
    (paper_dir / "mimo_raw_output.json").write_text(json.dumps(ir, ensure_ascii=False, indent=2), encoding="utf-8")
    ir = normalize_ir(ir, metadata, anchors)
    ir["verification"] = verify_ir(ir)
    report = quality_report(ir)

    for repair_round in range(1, 3):
        if report["passed"]:
            break
        ir = repair_ir_with_mimo(provider, ir, report, selected_blocks)
        (paper_dir / f"mimo_repair_round_{repair_round}.json").write_text(json.dumps(ir, ensure_ascii=False, indent=2), encoding="utf-8")
        ir = normalize_ir(ir, metadata, anchors)
        ir["verification"] = verify_ir(ir)
        report = quality_report(ir)

    ir_path.write_text(json.dumps(ir, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path = paper_dir / "quality_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report | {"status": "ok", "paper_id": spec["paper_id"], "title": spec["title"], "cached": False}


def pdf_url_candidates(spec: dict[str, Any]) -> list[str]:
    candidates = []
    for key in ["pdf_url", "open_access_pdf_url"]:
        value = spec.get(key)
        if isinstance(value, str) and value:
            candidates.append(value)
    arxiv_id = spec.get("arxiv_id")
    if arxiv_id:
        candidates.extend(
            [
                f"https://arxiv.org/pdf/{arxiv_id}",
                f"https://arxiv.org/pdf/{arxiv_id}.pdf",
            ]
        )
    fallback_urls = spec.get("fallback_pdf_urls") or []
    if isinstance(fallback_urls, list):
        candidates.extend([item for item in fallback_urls if isinstance(item, str) and item])
    deduped = []
    for item in candidates:
        if item not in deduped:
            deduped.append(item)
    return deduped


def download_pdf_candidates(urls: list[str], path: Path) -> None:
    errors = []
    for url in urls:
        try:
            download_pdf(url, path)
            return
        except Exception as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError("PDF download failed for all candidates: " + " | ".join(errors))


def download_pdf(url: str, path: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "zhiwei-benchmark/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            payload = response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"PDF download failed: {url}: {exc}") from exc
    if not payload.startswith(b"%PDF"):
        raise RuntimeError(f"Downloaded payload is not a PDF: {url}")
    path.write_bytes(payload)


def metadata_fallback_document(spec: dict[str, Any], reason: str) -> tuple[dict[str, Any], list[DocumentBlock]]:
    """Build a grounded minimal document when the original PDF cannot be fetched."""
    title = spec.get("title") or "unknown"
    authors = spec.get("authors") if isinstance(spec.get("authors"), list) else []
    abstract = spec.get("abstract") or "unknown"
    metadata = {
        "paper_id": spec["paper_id"],
        "title": title,
        "authors": authors,
        "venue": spec.get("venue"),
        "year": spec.get("year"),
        "arxiv_id": spec.get("arxiv_id"),
        "doi": spec.get("doi"),
        "language": "en",
        "source_mode": "metadata_abstract_fallback",
        "pdf_download_error": reason,
    }
    fallback_note = (
        "PDF download was unavailable for this benchmark run. "
        "This fallback source contains only paper metadata and the abstract from the selection index. "
        "Full-text formulas, tables, figures, ablations, and implementation details must be treated as unknown unless they appear here."
    )
    raw_blocks = [
        ("title", title, "Metadata"),
        ("paragraph", ", ".join(authors) if authors else "unknown authors", "Metadata"),
        (
            "paragraph",
            f"Year: {spec.get('year') or 'unknown'}; venue: {spec.get('venue') or 'unknown'}; paper type: {spec.get('paper_type') or 'unknown'}.",
            "Metadata",
        ),
        ("abstract", abstract, "Abstract"),
        ("paragraph", fallback_note, "Source Availability"),
    ]
    blocks = []
    for index, (block_type, content, section) in enumerate(raw_blocks, start=1):
        blocks.append(
            DocumentBlock(
                block_id=f"blk_{index:05d}",
                type=block_type,
                content=compact(str(content), 3500),
                page=1,
                section=section,
                bbox=None,
                anchor_id=f"anc_{index:05d}",
            )
        )
    return metadata, blocks


def anchors_from_blocks(blocks: list[DocumentBlock]) -> list[dict[str, Any]]:
    return [
        {
            "anchor_id": block.anchor_id,
            "page": block.page,
            "section": block.section,
            "bbox": block.bbox,
            "text_span": compact(block.content, 1000),
            "source_type": block.type if block.type in {"paragraph", "formula", "figure", "table", "caption", "reference"} else "paragraph",
        }
        for block in blocks
    ]


def block_to_json(block: DocumentBlock) -> dict[str, Any]:
    return {
        "block_id": block.block_id,
        "type": block.type,
        "content": block.content,
        "page": block.page,
        "section": block.section,
        "bbox": block.bbox,
        "anchor_id": block.anchor_id,
    }


def block_prompt_json(block: DocumentBlock) -> dict[str, Any]:
    return {
        "anchor_id": block.anchor_id,
        "page": block.page,
        "section": block.section,
        "type": block.type,
        "content": compact(block.content, 650),
    }


def select_context_blocks(blocks: list[DocumentBlock]) -> list[DocumentBlock]:
    keywords = [
        "abstract",
        "introduction",
        "propose",
        "we present",
        "we introduce",
        "method",
        "model",
        "architecture",
        "objective",
        "loss",
        "training",
        "inference",
        "experiment",
        "result",
        "ablation",
        "analysis",
        "table",
        "figure",
        "conclusion",
        "limitation",
        "baseline",
        "outperform",
        "evaluate",
        "dataset",
    ]
    scored: list[tuple[int, int, DocumentBlock]] = []
    for idx, block in enumerate(blocks):
        low = f"{block.section or ''} {block.type} {block.content}".lower()
        score = 0
        if block.page <= 2:
            score += 4
        if block.type in {"title", "abstract", "section_heading", "formula", "caption"}:
            score += 5
        if block.section in {"Abstract", "Introduction", "Method", "Experiments", "Results", "Limitations", "Conclusion"}:
            score += 3
        score += sum(2 for kw in keywords if kw and kw in low)
        if len(block.content) < 35:
            score -= 2
        scored.append((score, idx, block))

    top = sorted(scored, key=lambda x: (-x[0], x[1]))[:120]
    selected = sorted([item[2] for item in top], key=lambda b: (b.page, b.block_id))
    # Preserve the very first blocks even if extraction is messy.
    head = blocks[:20]
    merged = []
    seen = set()
    for block in head + selected:
        if block.anchor_id not in seen:
            merged.append(block)
            seen.add(block.anchor_id)
    return merged[:145]


def call_mimo_for_ir(provider: OpenAICompatibleProvider, payload: dict[str, Any]) -> dict[str, Any]:
    system = (
        "You are the Zhiwei Paper IR compiler. Use the provided document_blocks as the only source. "
        "Return strict JSON only, no Markdown. Every generated node or explanation must cite anchors."
    )
    user = f"""
Generate a complete Paper IR for this AI/LLM/machine-learning method paper, for the six Zhiwei modules.

Required coverage:
1. paper_skeleton: problem, motivation, core_idea, method, experiments, claims, limitations
2. method_graph: nodes and edges. node fields include node_id, title, label, summary, description, type, anchors
3. method_delta: baseline_method, new_method, deltas with before/after/why_it_matters/anchors
4. formula_ir: important formulas, variables, dependencies, intuition, anchors
5. experiment_matrix: main_result/ablation/robustness/scaling/case_study/human_eval/benchmark/efficiency
6. claim_evidence_map: 3-6 core claims, evidence source_type, support strength, anchors, risk_flags
7. glossary: context-specific terms
8. reproduction_roadmap: required datasets/models/compute/code_available/steps/missing_details/risk_points

Strict rules:
- All anchors must come from document_blocks.anchor_id.
- Do not present ungrounded strong conclusions as facts.
- Distinguish training-time and inference-time behavior.
- If a variable is inferred rather than explicitly defined by the paper, use confidence=medium or confidence=low.
- If exact formulas are not found in the extracted text, provide the core objective/loss/scoring formula as approximate LaTeX, mark relevant variables medium/low confidence, and anchor to related method paragraphs.
- Unknown implementation details must be written as unknown or missing_details.
- The JSON top level must be the Paper IR object.
- Prefer Chinese explanatory text for summaries, intuition, why_it_matters, and reproduction notes.

Input:
{json.dumps(payload, ensure_ascii=False)}
"""
    raw = provider.complete_json(system, user, {})
    if isinstance(raw, str):
        raw = json.loads(raw)
    if not isinstance(raw, dict):
        raise RuntimeError(f"Mimo returned non-object JSON: {type(raw).__name__}")
    return raw


def repair_ir_with_mimo(
    provider: OpenAICompatibleProvider,
    current_ir: dict[str, Any],
    report: dict[str, Any],
    selected_blocks: list[DocumentBlock],
) -> dict[str, Any]:
    system = (
        "You are the Zhiwei Paper IR repair compiler. Use only the provided current_ir and document_blocks. "
        "Return a complete corrected Paper IR JSON object. Do not output Markdown."
    )
    repair_ir = {key: value for key, value in current_ir.items() if key not in {"anchors", "verification"}}
    payload = {
        "quality_report": report,
        "current_ir": repair_ir,
        "document_blocks": [block_prompt_json(b) for b in selected_blocks],
        "repair_rules": [
            "Do not delete good existing content unless it violates source grounding.",
            "Fill missing experiment_matrix and reproduction_roadmap if absent.",
            "Every claim must have evidence with anchors.",
            "Every skeleton field, graph node, delta, formula, experiment, evidence, glossary term and reproduction step must cite anchors from document_blocks.",
            "Keep all analysis grounded in provided anchors only.",
        ],
    }
    user = f"""
The current Paper IR did not pass Zhiwei benchmark checks. Repair it.

Required final checks:
- problem/core_idea/method/experiments/claims exist
- method_delta exists
- formula_ir has important formulas
- experiment_matrix has main experiments and explains what each proves
- claim_evidence_map has evidence for every claim
- reproduction_roadmap has concrete steps and missing_details
- all method_graph nodes have anchors
- formula variables have confidence

Return the full repaired Paper IR object, not a diff.

Input:
{json.dumps(payload, ensure_ascii=False)}
"""
    raw = provider.complete_json(system, user, {})
    if isinstance(raw, str):
        raw = json.loads(raw)
    if not isinstance(raw, dict):
        raise RuntimeError(f"Mimo repair returned non-object JSON: {type(raw).__name__}")
    return raw


def parse_jsonish(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    if not stripped or stripped[0] not in "[{":
        return value
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return value


def as_object(value: Any, default: dict[str, Any] | None = None) -> dict[str, Any]:
    parsed = parse_jsonish(value)
    if isinstance(parsed, dict):
        return parsed
    return dict(default or {})


def as_list(value: Any) -> list[Any]:
    parsed = parse_jsonish(value)
    if isinstance(parsed, list):
        return parsed
    if parsed is None:
        return []
    return [parsed]


def object_list(value: Any) -> list[dict[str, Any]]:
    return [item for item in as_list(value) if isinstance(item, dict)]


def normalize_anchor_list(value: Any) -> list[str]:
    result: list[str] = []
    for item in as_list(value):
        if isinstance(item, str) and item:
            result.append(item)
        elif isinstance(item, dict):
            anchor = item.get("anchor_id") or item.get("id")
            if isinstance(anchor, str) and anchor:
                result.append(anchor)
    return result


def collect_nested_anchor_ids(value: Any) -> list[str]:
    found: list[str] = []

    def visit(item: Any) -> None:
        if isinstance(item, dict):
            for key in ["anchors", "source_anchors", "anchor_ids"]:
                found.extend(normalize_anchor_list(item.get(key)))
            for child in item.values():
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)

    visit(value)
    return list(dict.fromkeys(found))


def normalize_experiment(item: dict[str, Any], exp_type: str, index: int) -> dict[str, Any]:
    experiment = dict(item)
    experiment.setdefault("experiment_id", f"experiment_{index}")
    experiment.setdefault("type", exp_type)
    experiment.setdefault(
        "name",
        experiment.get("name")
        or experiment.get("experiment")
        or experiment.get("task")
        or experiment.get("variation")
        or experiment.get("aspect")
        or experiment.get("title")
        or f"{exp_type}_{index}",
    )
    experiment.setdefault("dataset", experiment.get("datasets") or [])
    experiment.setdefault("baseline", experiment.get("baselines") or [])
    metrics = experiment.get("metrics") or experiment.get("metric") or []
    experiment["metrics"] = metrics if isinstance(metrics, list) else [metrics]
    result_summary = (
        experiment.get("result_summary")
        or experiment.get("result")
        or experiment.get("finding")
        or experiment.get("findings")
        or experiment.get("key_findings")
        or experiment.get("observation")
        or experiment.get("value")
        or experiment.get("comparison")
        or experiment.get("evaluation")
        or experiment.get("summary")
        or experiment.get("description")
        or experiment.get("benchmark")
        or experiment.get("dimension")
        or ""
    )
    experiment["result_summary"] = result_summary
    what_it_proves = (
        experiment.get("what_it_tries_to_prove")
        or experiment.get("proves")
        or experiment.get("purpose")
        or experiment.get("what_it_proves")
        or experiment.get("interpretation")
        or experiment.get("comparison")
        or experiment.get("key_findings")
        or experiment.get("finding")
        or experiment.get("findings")
        or experiment.get("description")
        or result_summary
        or ""
    )
    experiment["what_it_tries_to_prove"] = what_it_proves
    experiment.setdefault("evidence_strength", experiment.get("support") or "unknown")
    direct_anchors = normalize_anchor_list(
        experiment.get("anchors") or experiment.get("source_anchors") or experiment.get("anchor_ids")
    )
    experiment["anchors"] = direct_anchors or collect_nested_anchor_ids(experiment)
    return experiment


def normalize_reproduction_step(item: Any, index: int) -> dict[str, Any]:
    if isinstance(item, dict):
        step = dict(item)
        step.setdefault("step", step.get("name") or f"step_{index}")
        step.setdefault("description", step.get("description") or step.get("detail") or step.get("text") or "")
    else:
        step = {"step": f"step_{index}", "description": str(item)}
    step["anchors"] = normalize_anchor_list(step.get("anchors") or step.get("source_anchors") or step.get("anchor_ids"))
    return step


def normalize_ir(ir: dict[str, Any], metadata: dict[str, Any], anchors: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(ir, dict):
        ir = {}
    for key in [
        "scope",
        "paper_skeleton",
        "method_graph",
        "method_delta",
        "formula_ir",
        "experiment_matrix",
        "claim_evidence_map",
        "glossary",
        "reproduction_roadmap",
        "visual_state",
    ]:
        ir[key] = parse_jsonish(ir.get(key))

    ir["schema_version"] = ir.get("schema_version") or "0.1.0"
    ir["generated_at"] = ir.get("generated_at") or now_iso()
    ir["generation_mode"] = "mimo_v2_5_pro_pipeline"
    ir["analysis_provider"] = {
        "provider": "openai_compatible",
        "model": LLM_MODEL,
        "base_url": LLM_BASE_URL,
        "api_key_loaded": bool(LLM_API_KEY),
        "note": "All Paper IR analysis fields are generated by the configured Mimo API. Local code only downloads PDFs, parses blocks, attaches anchors, normalizes JSON, and runs grounding verification.",
    }
    ir["metadata"] = metadata
    ir["anchors"] = anchors
    ir.setdefault("scope", {"supported_domain": "AI / LLM / machine learning method paper", "unsupported_domains": []})

    if isinstance(ir.get("method_graph"), list):
        ir["method_graph"] = {"nodes": ir["method_graph"], "edges": []}
    else:
        ir["method_graph"] = as_object(ir.get("method_graph"), {"nodes": [], "edges": []})
    ir["paper_skeleton"] = as_object(ir.get("paper_skeleton"), {})
    if isinstance(ir.get("method_delta"), list):
        ir["method_delta"] = {"baseline_method": {}, "new_method": {}, "deltas": ir["method_delta"]}
    else:
        ir["method_delta"] = as_object(ir.get("method_delta"), {"baseline_method": {}, "new_method": {}, "deltas": []})
    if isinstance(ir.get("formula_ir"), list):
        ir["formula_ir"] = {"formulas": ir["formula_ir"]}
    else:
        ir["formula_ir"] = as_object(ir.get("formula_ir"), {"formulas": []})
    if isinstance(ir.get("experiment_matrix"), list):
        ir["experiment_matrix"] = {"experiments": ir["experiment_matrix"]}
    else:
        ir["experiment_matrix"] = as_object(ir.get("experiment_matrix"), {"experiments": []})
    if isinstance(ir.get("claim_evidence_map"), list):
        ir["claim_evidence_map"] = {"claims": ir["claim_evidence_map"]}
    else:
        ir["claim_evidence_map"] = as_object(ir.get("claim_evidence_map"), {"claims": []})
    if isinstance(ir.get("glossary"), list):
        ir["glossary"] = {"terms": ir["glossary"]}
    else:
        ir["glossary"] = as_object(ir.get("glossary"), {"terms": []})
    ir["reproduction_roadmap"] = as_object(ir.get("reproduction_roadmap"), {"reproduction": {}})
    if "reproduction" not in ir["reproduction_roadmap"]:
        ir["reproduction_roadmap"] = {"reproduction": ir["reproduction_roadmap"]}
    ir["reproduction_roadmap"]["reproduction"] = as_object(ir["reproduction_roadmap"].get("reproduction"), {})

    for key in ["problem", "motivation", "core_idea", "method", "experiments"]:
        value = ir["paper_skeleton"].get(key)
        if isinstance(value, str):
            ir["paper_skeleton"][key] = {"summary": value, "anchors": []}
        elif not isinstance(value, dict):
            ir["paper_skeleton"][key] = {"summary": "", "anchors": []}
        else:
            value.setdefault("summary", value.get("description") or "")
            value["anchors"] = normalize_anchor_list(value.get("anchors") or value.get("source_anchors") or value.get("anchor_ids"))
    if isinstance(ir["paper_skeleton"].get("claims"), str):
        ir["paper_skeleton"]["claims"] = [
            {"claim_id": "claim_1", "claim": ir["paper_skeleton"]["claims"], "anchors": []}
        ]
    elif not isinstance(ir["paper_skeleton"].get("claims"), list):
        ir["paper_skeleton"]["claims"] = []
    ir["paper_skeleton"]["claims"] = [
        c if isinstance(c, dict) else {"claim_id": f"claim_{i}", "claim": str(c), "anchors": []}
        for i, c in enumerate(ir["paper_skeleton"].get("claims", []), start=1)
    ]
    for i, claim in enumerate(ir["paper_skeleton"]["claims"], start=1):
        claim.setdefault("claim_id", f"claim_{i}")
        claim.setdefault("claim", claim.get("summary") or "")
        claim["anchors"] = normalize_anchor_list(claim.get("anchors") or claim.get("source_anchors") or claim.get("anchor_ids"))
    if isinstance(ir["paper_skeleton"].get("limitations"), str):
        ir["paper_skeleton"]["limitations"] = [
            {"limitation": ir["paper_skeleton"]["limitations"], "anchors": []}
        ]
    elif not isinstance(ir["paper_skeleton"].get("limitations"), list):
        ir["paper_skeleton"]["limitations"] = []
    ir["paper_skeleton"]["limitations"] = [
        x if isinstance(x, dict) else {"limitation": str(x), "anchors": []}
        for x in ir["paper_skeleton"].get("limitations", [])
    ]
    for limitation in ir["paper_skeleton"]["limitations"]:
        limitation.setdefault("limitation", limitation.get("summary") or "")
        limitation["anchors"] = normalize_anchor_list(limitation.get("anchors") or limitation.get("source_anchors") or limitation.get("anchor_ids"))

    ir["method_graph"]["nodes"] = object_list(ir.get("method_graph", {}).get("nodes", []))
    ir["method_graph"]["edges"] = object_list(ir.get("method_graph", {}).get("edges", []))
    ir["method_delta"]["baseline_method"] = as_object(ir.get("method_delta", {}).get("baseline_method"), {})
    ir["method_delta"]["new_method"] = as_object(ir.get("method_delta", {}).get("new_method"), {})
    ir["method_delta"]["deltas"] = object_list(ir.get("method_delta", {}).get("deltas", []))
    for key in ["baseline_method", "new_method"]:
        ir["method_delta"][key]["anchors"] = normalize_anchor_list(
            ir["method_delta"][key].get("anchors")
            or ir["method_delta"][key].get("source_anchors")
            or ir["method_delta"][key].get("anchor_ids")
        )
    for i, delta in enumerate(ir["method_delta"]["deltas"], start=1):
        delta.setdefault("delta_id", f"delta_{i}")
        delta["anchors"] = normalize_anchor_list(delta.get("anchors") or delta.get("source_anchors") or delta.get("anchor_ids"))
    ir["formula_ir"]["formulas"] = object_list(ir.get("formula_ir", {}).get("formulas", []))
    for formula in ir["formula_ir"]["formulas"]:
        formula["variables"] = object_list(formula.get("variables", []))
        formula["dependencies"] = object_list(formula.get("dependencies", []))
        formula["anchors"] = normalize_anchor_list(formula.get("anchors") or formula.get("source_anchors") or formula.get("anchor_ids"))
        for variable in formula["variables"]:
            variable["anchors"] = normalize_anchor_list(variable.get("anchors") or variable.get("source_anchors") or variable.get("anchor_ids"))
            variable.setdefault("confidence", "low")
    experiment_items = []
    raw_experiments = object_list(ir.get("experiment_matrix", {}).get("experiments", []))
    if raw_experiments:
        for i, experiment in enumerate(raw_experiments, start=1):
            normalized = normalize_experiment(experiment, str(experiment.get("type") or "experiment"), i)
            if normalized.get("anchors") and (normalized.get("result_summary") or normalized.get("what_it_tries_to_prove")):
                experiment_items.append(normalized)
    else:
        for exp_type in ["main_result", "ablation", "robustness", "scaling", "case_study", "human_eval", "benchmark", "efficiency"]:
            for experiment in object_list(ir.get("experiment_matrix", {}).get(exp_type, [])):
                normalized = normalize_experiment(experiment, exp_type, len(experiment_items) + 1)
                if normalized.get("anchors") and (normalized.get("result_summary") or normalized.get("what_it_tries_to_prove")):
                    experiment_items.append(normalized)
    ir["experiment_matrix"]["experiments"] = experiment_items
    ir["claim_evidence_map"]["claims"] = object_list(ir.get("claim_evidence_map", {}).get("claims", []))
    for i, claim in enumerate(ir["claim_evidence_map"]["claims"], start=1):
        claim.setdefault("claim_id", f"claim_{i}")
        claim["anchors"] = normalize_anchor_list(claim.get("anchors") or claim.get("source_anchors") or claim.get("anchor_ids"))
        claim["evidence"] = object_list(claim.get("evidence", []))
        for j, evidence in enumerate(claim["evidence"], start=1):
            evidence.setdefault("evidence_id", f"{claim['claim_id']}_evidence_{j}")
            evidence["anchors"] = normalize_anchor_list(evidence.get("anchors") or evidence.get("source_anchors") or evidence.get("anchor_ids"))
        claim.setdefault("risk_flags", [])
    ir["glossary"]["terms"] = object_list(ir.get("glossary", {}).get("terms", []))
    for term in ir["glossary"]["terms"]:
        term["appears_in"] = normalize_anchor_list(term.get("appears_in") or term.get("anchors") or term.get("source_anchors"))
    reproduction = ir["reproduction_roadmap"]["reproduction"]
    step_source = reproduction.get("steps") or reproduction.get("reproduction_steps") or []
    reproduction["steps"] = [normalize_reproduction_step(step, i) for i, step in enumerate(as_list(step_source), start=1)]
    reproduction["missing_details"] = object_list(reproduction.get("missing_details", []))
    for detail in reproduction["missing_details"]:
        detail["anchors"] = normalize_anchor_list(detail.get("anchors") or detail.get("source_anchors") or detail.get("anchor_ids"))
    reproduction["risk_points"] = object_list(reproduction.get("risk_points", []))

    for node in ir.get("method_graph", {}).get("nodes", []):
        if not isinstance(node, dict):
            continue
        node.setdefault("title", node.get("label") or node.get("node_id") or "node")
        node.setdefault("label", node.get("title"))
        node.setdefault("summary", node.get("description") or "")
        node.setdefault("description", node.get("summary") or "")
        node["anchors"] = normalize_anchor_list(node.get("anchors") or node.get("source_anchors") or node.get("anchor_ids"))
    for edge in ir.get("method_graph", {}).get("edges", []):
        if not isinstance(edge, dict):
            continue
        edge["anchors"] = normalize_anchor_list(edge.get("anchors") or edge.get("source_anchors") or edge.get("anchor_ids"))
        edge.setdefault("description", edge.get("relation", ""))

    ir.setdefault("paper_skeleton", {})
    ir.setdefault("method_graph", {"nodes": [], "edges": []})
    ir.setdefault("method_delta", {"baseline_method": {}, "new_method": {}, "deltas": []})
    ir.setdefault("formula_ir", {"formulas": []})
    ir.setdefault("experiment_matrix", {"experiments": []})
    ir.setdefault("claim_evidence_map", {"claims": []})
    ir.setdefault("glossary", {"terms": []})
    ir.setdefault("reproduction_roadmap", {"reproduction": {}})
    return ir


def quality_report(ir: dict[str, Any]) -> dict[str, Any]:
    verification = ir.get("verification") or verify_ir(ir)
    skeleton = as_object(ir.get("paper_skeleton"), {})
    graph = as_object(ir.get("method_graph"), {})
    formulas = object_list(as_object(ir.get("formula_ir"), {}).get("formulas", []))
    claims = object_list(as_object(ir.get("claim_evidence_map"), {}).get("claims", []))
    experiments = object_list(as_object(ir.get("experiment_matrix"), {}).get("experiments", []))
    deltas = object_list(as_object(ir.get("method_delta"), {}).get("deltas", []))
    reproduction = as_object(as_object(ir.get("reproduction_roadmap"), {}).get("reproduction"), {})
    repro_steps = object_list(reproduction.get("steps", []))
    nodes = object_list(graph.get("nodes", []))
    all_nodes_have_anchors = bool(nodes) and all(bool(node.get("anchors")) for node in nodes)
    all_claims_have_evidence = bool(claims) and all(bool(object_list(claim.get("evidence"))) for claim in claims)
    formula_variables_have_confidence = all(
        var.get("confidence") in {"high", "medium", "low"}
        for formula in formulas
        for var in object_list(formula.get("variables", []))
    )
    checks = {
        "has_problem": bool(as_object(skeleton.get("problem"), {}).get("summary")),
        "has_core_idea": bool(as_object(skeleton.get("core_idea"), {}).get("summary")),
        "has_method": bool(as_object(skeleton.get("method"), {}).get("summary")),
        "has_experiments": bool(as_object(skeleton.get("experiments"), {}).get("summary")),
        "has_claims": bool(claims),
        "has_method_delta": bool(deltas),
        "has_formulas": bool(formulas),
        "has_experiment_matrix": bool(experiments),
        "has_reproduction": bool(repro_steps),
        "all_nodes_have_anchors": all_nodes_have_anchors,
        "all_claims_have_evidence": all_claims_have_evidence,
        "formula_variables_have_confidence": formula_variables_have_confidence,
    }
    warning_count = len([w for w in verification.get("warnings", []) if w.get("severity") != "info"])
    return {
        "paper_id": ir.get("metadata", {}).get("paper_id"),
        "title": ir.get("metadata", {}).get("title"),
        "anchor_count": len(ir.get("anchors", [])),
        "node_count": len(nodes),
        "delta_count": len(deltas),
        "formula_count": len(formulas),
        "claim_count": len(claims),
        "experiment_count": len(experiments),
        "reproduction_step_count": len(repro_steps),
        "verification_status": verification.get("status"),
        "warning_count": warning_count,
        "checks": checks,
        "passed": all(checks.values()) and warning_count == 0,
    }


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
