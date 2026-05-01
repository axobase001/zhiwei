from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from .benchmark_pipeline import OUT_DIR, PAPERS, ensure_api_config, run_one
from .config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, PROJECT_ROOT
from .llm import OpenAICompatibleProvider
from .utils import now_iso


S2_ENDPOINT = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
TOP_DIR = PROJECT_ROOT / "samples" / "benchmark" / "top_ml"
SPEC_PATH = TOP_DIR / "top_ml_specs.json"
TOP100_PATH = TOP_DIR / "top100_candidates.json"
SUMMARY_PATH = TOP_DIR / "top_ml_pipeline_summary.json"

SEARCH_QUERIES = [
    "machine learning",
    "deep learning",
    "neural network",
    "convolutional neural network",
    "recurrent neural network",
    "representation learning",
    "computer vision",
    "natural language processing",
    "reinforcement learning",
    "support vector",
    "random forest",
    "gradient boosting",
    "generative adversarial networks",
    "variational autoencoder",
    "graph neural network",
    "transformer",
]

EXCLUDE_TITLE_RE = re.compile(
    r"\b("
    r"survey|review|overview|systematic review|bibliometric|meta-analysis|tutorial|primer|roadmap|perspective|"
    r"protein|alphafold|biomolecular|phylogen\w*|molecular|genetic|biomedical|medical|clinical|surgery|toxicity|cancer|disease"
    r")\b",
    re.I,
)
METHOD_HINT_RE = re.compile(
    r"\b("
    r"algorithm|model|network|neural|learning|training|optimization|classifier|classification|regression|"
    r"attention|transformer|embedding|representation|boosting|forest|support vector|bayesian|"
    r"convolutional|recurrent|adversarial|autoencoder|reinforcement|gradient|detection|segmentation|"
    r"translation|recognition|generation|pre-training|pretraining"
    r")\b",
    re.I,
)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Build and run a top-cited ML Paper IR benchmark from Semantic Scholar.")
    parser.add_argument("--top", type=int, default=100, help="Number of top cited ML candidates before excluding existing papers.")
    parser.add_argument("--offset", type=int, default=0, help="Skip this many selected specs before running.")
    parser.add_argument("--run-limit", type=int, default=0, help="Run at most this many new papers. 0 means all selected specs.")
    parser.add_argument("--fetch-only", action="store_true", help="Only fetch and write specs, do not call Mimo pipeline.")
    parser.add_argument("--force", action="store_true", help="Regenerate existing generated papers.")
    parser.add_argument("--sleep", type=float, default=1.0, help="Sleep seconds between Semantic Scholar/API calls.")
    args = parser.parse_args(argv)

    TOP_DIR.mkdir(parents=True, exist_ok=True)
    candidates = fetch_top_candidates(args.top, sleep=args.sleep)
    existing = existing_keys()
    selected = [paper_to_spec(paper, rank) for rank, paper in enumerate(candidates, start=1) if not is_existing(paper, existing)]
    selected = [spec for spec in selected if spec.get("pdf_url")]
    if args.offset:
        selected = selected[args.offset :]
    if args.run_limit > 0:
        selected = selected[: args.run_limit]

    TOP100_PATH.write_text(json.dumps({"generated_at": now_iso(), "source": source_note(), "papers": candidates}, ensure_ascii=False, indent=2), encoding="utf-8")
    SPEC_PATH.write_text(json.dumps({"generated_at": now_iso(), "source": source_note(), "papers": selected}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"top candidates: {len(candidates)} -> {TOP100_PATH}", flush=True)
    print(f"selected new specs: {len(selected)} -> {SPEC_PATH}", flush=True)

    if args.fetch_only:
        return 0

    ensure_api_config()
    provider = OpenAICompatibleProvider(LLM_BASE_URL, LLM_API_KEY, LLM_MODEL)
    summary = []
    for index, spec in enumerate(selected, start=1):
        print(f"[{index}/{len(selected)}] rank={spec.get('importance_rank')} citations={spec.get('citation_count')} {spec['paper_id']} :: {spec['title']}", flush=True)
        try:
            result = run_one(spec, provider, force=args.force, skip_download=False)
            result["importance_rank"] = spec.get("importance_rank")
            result["citation_count"] = spec.get("citation_count")
            summary.append(result)
            print(f"  ok anchors={result['anchor_count']} formulas={result['formula_count']} warnings={result['warning_count']}", flush=True)
        except Exception as exc:
            item = {
                "paper_id": spec["paper_id"],
                "title": spec["title"],
                "importance_rank": spec.get("importance_rank"),
                "citation_count": spec.get("citation_count"),
                "status": "failed",
                "error": str(exc),
            }
            summary.append(item)
            print(f"  failed: {exc}", flush=True)
        SUMMARY_PATH.write_text(json.dumps({"generated_at": now_iso(), "model": LLM_MODEL, "papers": summary}, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(args.sleep)
    print(f"summary: {SUMMARY_PATH}", flush=True)
    return 0


def source_note() -> dict[str, Any]:
    return {
        "name": "Semantic Scholar Academic Graph API",
        "endpoint": S2_ENDPOINT,
        "sort": "citationCount:desc",
        "openAccessPdf": True,
        "fields": "title,authors,year,venue,citationCount,influentialCitationCount,externalIds,openAccessPdf,fieldsOfStudy,publicationTypes,abstract,url",
        "queries": SEARCH_QUERIES,
        "filtering": "Deduplicate by Semantic Scholar paperId; keep method-like ML/AI papers with downloadable PDFs; exclude existing local papers and obvious surveys/reviews.",
    }


def fetch_top_candidates(top: int, sleep: float) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for query in SEARCH_QUERIES:
        for paper in s2_search(query):
            if not keep_candidate(paper):
                continue
            key = paper.get("paperId") or title_key(paper.get("title", ""))
            if not key:
                continue
            if key not in seen or citation_count(paper) > citation_count(seen[key]):
                seen[key] = paper
        time.sleep(sleep)
    return sorted(seen.values(), key=citation_count, reverse=True)[:top]


def s2_search(query: str) -> list[dict[str, Any]]:
    params = {
        "query": query,
        "fields": "title,authors,year,venue,citationCount,influentialCitationCount,externalIds,openAccessPdf,fieldsOfStudy,publicationTypes,abstract,url",
        "openAccessPdf": "true",
        "sort": "citationCount:desc",
        "fieldsOfStudy": "Computer Science",
    }
    url = S2_ENDPOINT + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "zhiwei-top-ml/0.1"})
    with urllib.request.urlopen(req, timeout=90) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("data", [])


def keep_candidate(paper: dict[str, Any]) -> bool:
    if not paper.get("title") or citation_count(paper) <= 0:
        return False
    if not paper.get("openAccessPdf", {}).get("url") and not paper.get("externalIds", {}).get("ArXiv"):
        return False
    title = paper.get("title") or ""
    abstract = paper.get("abstract") or ""
    if EXCLUDE_TITLE_RE.search(title):
        return False
    fields = set(paper.get("fieldsOfStudy") or [])
    if "Computer Science" not in fields and not METHOD_HINT_RE.search(title + " " + abstract):
        return False
    if not METHOD_HINT_RE.search(title + " " + abstract):
        return False
    return True


def existing_keys() -> set[str]:
    keys: set[str] = set()
    for spec in PAPERS:
        keys.add(title_key(spec.get("title", "")))
        if spec.get("arxiv_id"):
            keys.add("arxiv:" + str(spec["arxiv_id"]).lower())
    for ir_path in OUT_DIR.glob("*/paper_ir.json"):
        try:
            ir = json.loads(ir_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        meta = ir.get("metadata") or {}
        keys.add(title_key(meta.get("title", "")))
        if meta.get("arxiv_id"):
            keys.add("arxiv:" + str(meta["arxiv_id"]).lower())
        if meta.get("semantic_scholar_id"):
            keys.add("s2:" + str(meta["semantic_scholar_id"]))
    return keys


def is_existing(paper: dict[str, Any], keys: set[str]) -> bool:
    external = paper.get("externalIds") or {}
    checks = {title_key(paper.get("title", ""))}
    if external.get("ArXiv"):
        checks.add("arxiv:" + str(external["ArXiv"]).lower())
    if paper.get("paperId"):
        checks.add("s2:" + str(paper["paperId"]))
    return any(item in keys for item in checks if item)


def paper_to_spec(paper: dict[str, Any], rank: int) -> dict[str, Any]:
    external = paper.get("externalIds") or {}
    arxiv_id = external.get("ArXiv")
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else paper.get("openAccessPdf", {}).get("url")
    authors = [author.get("name") for author in paper.get("authors", []) if author.get("name")]
    title = paper.get("title") or f"paper {rank}"
    return {
        "paper_id": f"paper_ml_{rank:03d}_{slugify(title)}_{paper.get('year') or 'unknown'}",
        "title": title,
        "authors": authors[:12] or ["unknown"],
        "year": paper.get("year"),
        "venue": paper.get("venue"),
        "arxiv_id": arxiv_id,
        "doi": external.get("DOI"),
        "paper_type": classify_paper_type(paper),
        "pdf_url": pdf_url,
        "citation_count": paper.get("citationCount"),
        "influential_citation_count": paper.get("influentialCitationCount"),
        "semantic_scholar_id": paper.get("paperId"),
        "semantic_scholar_url": paper.get("url"),
        "importance_rank": rank,
        "selection_source": "semantic_scholar_top_cited_ml_open_pdf_2026_05_01",
        "open_access_pdf_url": paper.get("openAccessPdf", {}).get("url"),
        "fields_of_study": paper.get("fieldsOfStudy") or [],
        "publication_types": paper.get("publicationTypes") or [],
        "abstract": paper.get("abstract"),
    }


def classify_paper_type(paper: dict[str, Any]) -> str:
    text = f"{paper.get('title') or ''} {paper.get('abstract') or ''}".lower()
    labels = []
    for keyword, label in [
        ("transformer", "Transformer"),
        ("attention", "Attention"),
        ("reinforcement", "Reinforcement Learning"),
        ("convolution", "Computer Vision / CNN"),
        ("object detection", "Computer Vision / Detection"),
        ("segmentation", "Computer Vision / Segmentation"),
        ("language", "NLP"),
        ("translation", "NLP / Machine Translation"),
        ("generative adversarial", "Generative Models / GAN"),
        ("autoencoder", "Generative Models / Autoencoder"),
        ("support vector", "Classical ML / SVM"),
        ("random forest", "Classical ML / Random Forest"),
        ("boost", "Classical ML / Boosting"),
        ("graph neural", "Graph ML"),
    ]:
        if keyword in text:
            labels.append(label)
    labels.append("Top-cited ML method paper")
    return " / ".join(dict.fromkeys(labels))


def title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    return slug[:48] or "paper"


def citation_count(paper: dict[str, Any]) -> int:
    try:
        return int(paper.get("citationCount") or 0)
    except (TypeError, ValueError):
        return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
