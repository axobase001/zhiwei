from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from .benchmark_pipeline import ensure_api_config, run_one
from .config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, PROJECT_ROOT
from .llm import OpenAICompatibleProvider
from .semantic_ml_pipeline import citation_count, existing_keys, is_existing, slugify, title_key
from .utils import now_iso


S2_ENDPOINT = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
TOP_DIR = PROJECT_ROOT / "samples" / "benchmark" / "top_cv"
SPEC_PATH = TOP_DIR / "top_cv_specs.json"
TOP_CANDIDATES_PATH = TOP_DIR / "top_cv_candidates.json"
SUMMARY_PATH = TOP_DIR / "top_cv_pipeline_summary.json"

SEARCH_QUERIES = [
    "computer vision",
    "image recognition",
    "image classification",
    "object detection",
    "semantic segmentation",
    "instance segmentation",
    "visual recognition",
    "convolutional neural network computer vision",
    "face recognition",
    "pose estimation",
    "visual object tracking",
    "video classification",
    "action recognition video",
    "optical flow",
    "depth estimation",
    "image retrieval",
    "image captioning",
    "visual question answering",
    "vision transformer",
    "self-supervised visual representation",
    "contrastive visual learning",
    "generative adversarial network image",
    "image generation",
    "super resolution",
    "multimodal vision language",
    "visual dataset benchmark",
]

EXCLUDE_TITLE_RE = re.compile(
    r"\b("
    r"survey|review|overview|systematic review|bibliometric|meta-analysis|tutorial|primer|roadmap|perspective|"
    r"medical|clinical|surgery|cancer|disease|diseases|pathology|radiology|x-ray|chest|thorax|protein|molecular|genetic|biomedical|bioinformatics|"
    r"remote sensing review|machine translation|statistical data visualization|seaborn|rare words|subword units|"
    r"speech recognition|text categorization|sentiment classification|support vector machines|"
    r"recent advances|imagej|human connectome|natural language inference|eegnet|text classification|"
    r"universal language model|soilgrids|guided search|robust principal component analysis|"
    r"deep learning[: ]+methods and applications|geometric deep learning|adversarial settings|soilgrids\w*|"
    r"time series|forecasting"
    r")\b",
    re.I,
)

EXCLUDE_VENUE_RE = re.compile(
    r"\b("
    r"bioinformatics|neuroimage|psychology|psychonomic|security and privacy|natural language processing|"
    r"empirical methods in natural language processing|association for computational linguistics"
    r")\b",
    re.I,
)

CV_HINT_RE = re.compile(
    r"\b("
    r"computer vision|image|images|visual|vision|video|videos|object detection|detection|segmentation|recognition|"
    r"classification|tracking|pose|optical flow|depth|scene|face|faces|captioning|visual question|vqa|"
    r"convolutional|cnn|faster r-cnn|mask r-cnn|yolo|ssd|resnet|imagenet|coco|cityscapes|pascal|"
    r"gan|generative adversarial|super-resolution|diffusion|clip|multimodal|vision-language|vision transformer|vit|"
    r"self-supervised|contrastive"
    r")\b",
    re.I,
)

CV_TITLE_HINT_RE = re.compile(
    r"\b("
    r"image|images|visual|vision|video|object|detection|segmentation|recognition|tracking|pose|optical flow|depth|"
    r"scene|face|faces|caption|vqa|convolutional|cnn|r-cnn|yolo|ssd|resnet|imagenet|coco|cityscapes|pascal|"
    r"gan|super-resolution|diffusion|clip|multimodal|vision-language|vision transformer|vit|self-supervised|"
    r"contrastive|inpainting|bounding box|openpose|kitti|sift|hog|shape context|edge"
    r")\b",
    re.I,
)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Build and run a top-cited Computer Vision Paper IR benchmark.")
    parser.add_argument("--pool", type=int, default=260, help="Candidate pool size before excluding existing papers.")
    parser.add_argument("--target-new", type=int, default=100, help="Number of non-existing CV papers to keep in specs.")
    parser.add_argument("--offset", type=int, default=0, help="Skip this many selected specs before running.")
    parser.add_argument("--run-limit", type=int, default=0, help="Run at most this many selected specs. 0 means all.")
    parser.add_argument("--fetch-only", action="store_true", help="Only fetch and write specs, do not call Mimo.")
    parser.add_argument("--use-existing-specs", action="store_true", help="Use samples/benchmark/top_cv/top_cv_specs.json without refetching Semantic Scholar.")
    parser.add_argument("--missing-only", action="store_true", help="Run only specs that are not already marked ok in the summary.")
    parser.add_argument("--force", action="store_true", help="Regenerate existing generated papers.")
    parser.add_argument("--sleep", type=float, default=1.0, help="Sleep seconds between Semantic Scholar/API calls.")
    args = parser.parse_args(argv)

    TOP_DIR.mkdir(parents=True, exist_ok=True)
    if args.use_existing_specs:
        selected = load_existing_specs()
        candidates = load_existing_candidates()
    else:
        candidates = fetch_top_candidates(args.pool, sleep=args.sleep)
        existing = existing_keys()
        selected = []
        for rank, paper in enumerate(candidates, start=1):
            if is_existing(paper, existing):
                continue
            spec = paper_to_spec(paper, rank)
            if spec.get("pdf_url"):
                selected.append(spec)
            if len(selected) >= args.target_new:
                break

    run_specs = selected[args.offset :]
    if args.missing_only:
        completed = {
            item.get("paper_id")
            for item in load_existing_summary()
            if item.get("paper_id") and item.get("status") in {"ok", "failed", "skipped"}
        }
        run_specs = [spec for spec in run_specs if spec.get("paper_id") not in completed]
    if args.run_limit > 0:
        run_specs = run_specs[: args.run_limit]

    if not args.use_existing_specs:
        TOP_CANDIDATES_PATH.write_text(
            json.dumps({"generated_at": now_iso(), "source": source_note(), "papers": candidates}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        SPEC_PATH.write_text(
            json.dumps({"generated_at": now_iso(), "source": source_note(), "papers": selected}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    print(f"cv candidates: {len(candidates)} -> {TOP_CANDIDATES_PATH}", flush=True)
    print(f"selected new specs: {len(selected)} -> {SPEC_PATH}", flush=True)
    print(f"run specs: {len(run_specs)} offset={args.offset} limit={args.run_limit}", flush=True)

    if args.fetch_only:
        return 0

    ensure_api_config()
    provider = OpenAICompatibleProvider(LLM_BASE_URL, LLM_API_KEY, LLM_MODEL)
    summary = load_existing_summary()
    by_id = {item.get("paper_id"): item for item in summary if item.get("paper_id")}
    for index, spec in enumerate(run_specs, start=1):
        print(
            f"[{index}/{len(run_specs)}] rank={spec.get('importance_rank')} citations={spec.get('citation_count')} "
            f"{spec['paper_id']} :: {spec['title']}",
            flush=True,
        )
        try:
            result = run_one(spec, provider, force=args.force, skip_download=False)
            result["importance_rank"] = spec.get("importance_rank")
            result["citation_count"] = spec.get("citation_count")
            result["status"] = "ok"
            by_id[spec["paper_id"]] = result
            print(
                f"  ok anchors={result['anchor_count']} formulas={result['formula_count']} warnings={result['warning_count']}",
                flush=True,
            )
        except Exception as exc:
            by_id[spec["paper_id"]] = {
                "paper_id": spec["paper_id"],
                "title": spec["title"],
                "importance_rank": spec.get("importance_rank"),
                "citation_count": spec.get("citation_count"),
                "status": "failed",
                "error": str(exc),
            }
            print(f"  failed: {exc}", flush=True)
        write_summary(list(by_id.values()))
        time.sleep(args.sleep)
    write_summary(list(by_id.values()))
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
        "filtering": "Deduplicate by Semantic Scholar paperId; keep computer-vision papers with downloadable PDFs; exclude existing local papers and obvious surveys/reviews/non-CV biomedical papers.",
    }


def fetch_top_candidates(pool: int, sleep: float) -> list[dict[str, Any]]:
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
    return sorted(seen.values(), key=citation_count, reverse=True)[:pool]


def s2_search(query: str) -> list[dict[str, Any]]:
    params = {
        "query": query,
        "fields": "title,authors,year,venue,citationCount,influentialCitationCount,externalIds,openAccessPdf,fieldsOfStudy,publicationTypes,abstract,url",
        "openAccessPdf": "true",
        "sort": "citationCount:desc",
        "fieldsOfStudy": "Computer Science",
    }
    url = S2_ENDPOINT + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "zhiwei-top-cv/0.1"})
    for attempt in range(1, 5):
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return payload.get("data", [])
        except urllib.error.HTTPError as exc:
            if exc.code in {429, 500, 502, 503, 504} and attempt < 4:
                time.sleep(2 * attempt)
                continue
            raise
        except urllib.error.URLError:
            if attempt < 4:
                time.sleep(2 * attempt)
                continue
            raise
    return []


def keep_candidate(paper: dict[str, Any]) -> bool:
    if not paper.get("title") or citation_count(paper) <= 0:
        return False
    external = paper.get("externalIds") or {}
    if not paper.get("openAccessPdf", {}).get("url") and not external.get("ArXiv"):
        return False
    title = paper.get("title") or ""
    abstract = paper.get("abstract") or ""
    venue = paper.get("venue") or ""
    text = f"{title} {abstract}"
    if EXCLUDE_TITLE_RE.search(title):
        return False
    if EXCLUDE_VENUE_RE.search(venue) and not re.search(r"\b(computer vision|image processing|pattern analysis)\b", venue, re.I):
        return False
    if not CV_TITLE_HINT_RE.search(title) and not CV_HINT_RE.search(text):
        return False
    return True


def paper_to_spec(paper: dict[str, Any], rank: int) -> dict[str, Any]:
    external = paper.get("externalIds") or {}
    arxiv_id = external.get("ArXiv")
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else paper.get("openAccessPdf", {}).get("url")
    authors = [author.get("name") for author in paper.get("authors", []) if author.get("name")]
    title = paper.get("title") or f"paper {rank}"
    return {
        "paper_id": f"paper_cv_{rank:03d}_{slugify(title)}_{paper.get('year') or 'unknown'}",
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
        "selection_source": "semantic_scholar_top_cited_cv_open_pdf_2026_05_03",
        "open_access_pdf_url": paper.get("openAccessPdf", {}).get("url"),
        "fields_of_study": paper.get("fieldsOfStudy") or [],
        "publication_types": paper.get("publicationTypes") or [],
        "abstract": paper.get("abstract"),
    }


def classify_paper_type(paper: dict[str, Any]) -> str:
    text = f"{paper.get('title') or ''} {paper.get('abstract') or ''}".lower()
    labels = []
    for keyword, label in [
        ("object detection", "Computer Vision / Object Detection"),
        ("segmentation", "Computer Vision / Segmentation"),
        ("face", "Computer Vision / Face Recognition"),
        ("pose", "Computer Vision / Pose Estimation"),
        ("tracking", "Computer Vision / Tracking"),
        ("video", "Computer Vision / Video Understanding"),
        ("caption", "Vision-Language / Captioning"),
        ("visual question", "Vision-Language / VQA"),
        ("vision-language", "Vision-Language"),
        ("multimodal", "Vision-Language / Multimodal"),
        ("transformer", "Computer Vision / Transformer"),
        ("attention", "Computer Vision / Attention"),
        ("generative adversarial", "Computer Vision / Generative Models"),
        ("diffusion", "Computer Vision / Diffusion"),
        ("self-supervised", "Computer Vision / Self-Supervised Learning"),
        ("contrastive", "Computer Vision / Contrastive Learning"),
        ("convolution", "Computer Vision / CNN"),
        ("image", "Computer Vision"),
    ]:
        if keyword in text:
            labels.append(label)
    labels.append("Top-cited Computer Vision paper")
    return " / ".join(dict.fromkeys(labels))


def load_existing_summary() -> list[dict[str, Any]]:
    if not SUMMARY_PATH.exists():
        return []
    try:
        data = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    papers = data.get("papers")
    return papers if isinstance(papers, list) else []


def load_existing_specs() -> list[dict[str, Any]]:
    if not SPEC_PATH.exists():
        raise RuntimeError(f"Missing existing spec file: {SPEC_PATH}")
    data = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    papers = data.get("papers")
    if not isinstance(papers, list):
        raise RuntimeError(f"Invalid existing spec file: {SPEC_PATH}")
    return [item for item in papers if isinstance(item, dict)]


def load_existing_candidates() -> list[dict[str, Any]]:
    if not TOP_CANDIDATES_PATH.exists():
        return []
    try:
        data = json.loads(TOP_CANDIDATES_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    papers = data.get("papers")
    return papers if isinstance(papers, list) else []


def write_summary(papers: list[dict[str, Any]]) -> None:
    SUMMARY_PATH.write_text(
        json.dumps({"generated_at": now_iso(), "model": LLM_MODEL, "papers": papers}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
