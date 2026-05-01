from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .utils import clean_text, compact


SECTION_CANON = {
    "abstract": "Abstract",
    "introduction": "Introduction",
    "related work": "Related Work",
    "background": "Related Work",
    "method": "Method",
    "methods": "Method",
    "methodology": "Method",
    "approach": "Method",
    "model": "Method",
    "experiments": "Experiments",
    "experiment": "Experiments",
    "experimental setup": "Experiments",
    "results": "Results",
    "evaluation": "Results",
    "discussion": "Discussion",
    "limitations": "Limitations",
    "conclusion": "Conclusion",
    "conclusions": "Conclusion",
    "references": "References",
}


@dataclass
class DocumentBlock:
    block_id: str
    type: str
    content: str
    page: int
    section: str | None
    bbox: dict[str, float] | None
    anchor_id: str


def read_pdf_pages(path: Path) -> list[str]:
    try:
        from pypdf import PdfReader
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("缺少 pypdf。请运行 pip install -r requirements.txt") from exc

    reader = PdfReader(str(path))
    pages: list[str] = []
    for page in reader.pages:
        try:
            pages.append(clean_text(page.extract_text() or ""))
        except Exception:
            pages.append("")
    return pages


def classify_section(raw: str) -> str | None:
    text = re.sub(r"^\s*\d+(\.\d+)*\s+", "", raw).strip().lower()
    text = re.sub(r"[^a-z ]", "", text)
    if text in SECTION_CANON:
        return SECTION_CANON[text]
    for key, value in SECTION_CANON.items():
        if text.startswith(key) and len(text) <= len(key) + 18:
            return value
    return None


def is_heading(line: str) -> bool:
    line = line.strip()
    if not line or len(line) > 90:
        return False
    if classify_section(line):
        return True
    if re.match(r"^\d+(\.\d+)*\s+[A-Z][A-Za-z0-9 ,:/&()\-]{2,}$", line):
        return True
    return False


def block_type_for(content: str, current_section: str | None, page: int, index_on_page: int) -> str:
    low = content.strip().lower()
    if page == 1 and index_on_page == 0:
        return "title"
    if classify_section(content):
        return "section_heading"
    if low.startswith(("figure ", "fig. ", "table ")):
        return "caption"
    if current_section == "References":
        return "reference"
    if looks_like_formula(content):
        return "formula"
    return "paragraph"


def looks_like_formula(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) > 260:
        return False
    math_marks = ["=", "\\", "∑", "Σ", "∏", "∇", "≤", "≥", "≈", "arg", "log", "softmax", "max", "min"]
    if any(mark in stripped for mark in math_marks):
        symbol_count = len(re.findall(r"[A-Za-zα-ωΑ-Ω][_\^\{\}\w]*", stripped))
        return symbol_count >= 2
    return False


def split_page(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines()]
    blocks: list[str] = []
    buf: list[str] = []

    def flush() -> None:
        nonlocal buf
        joined = clean_text(" ".join(buf))
        if joined:
            blocks.append(joined)
        buf = []

    for line in lines:
        if not line:
            flush()
            continue
        if is_heading(line) or line.lower().startswith(("figure ", "fig. ", "table ")):
            flush()
            blocks.append(line)
            continue
        if looks_like_formula(line):
            flush()
            blocks.append(line)
            continue
        buf.append(line)
    flush()
    return blocks


def parse_pdf(path: Path, paper_id: str) -> tuple[dict[str, Any], list[DocumentBlock]]:
    pages = read_pdf_pages(path)
    blocks: list[DocumentBlock] = []
    current_section: str | None = None
    title = "未命名论文"
    authors: list[str] = []

    anchor_counter = 1
    for page_num, page_text in enumerate(pages, start=1):
        page_blocks = split_page(page_text)
        for idx, content in enumerate(page_blocks):
            section_hit = classify_section(content)
            block_type = block_type_for(content, current_section, page_num, idx)
            if section_hit:
                current_section = section_hit
            if page_num == 1 and block_type == "title":
                title = compact(content, 220)
            elif page_num == 1 and not authors and idx in (1, 2) and block_type == "paragraph":
                possible = [p.strip() for p in re.split(r",| and |;|\n", content) if p.strip()]
                if 1 <= len(possible) <= 16 and len(content) < 260:
                    authors = possible[:12]

            anchor_id = f"anc_{anchor_counter:05d}"
            block_id = f"blk_{anchor_counter:05d}"
            anchor_counter += 1
            blocks.append(
                DocumentBlock(
                    block_id=block_id,
                    type=block_type,
                    content=content,
                    page=page_num,
                    section=current_section,
                    bbox=None,
                    anchor_id=anchor_id,
                )
            )

    metadata = {
        "paper_id": paper_id,
        "title": title,
        "authors": authors,
        "venue": None,
        "year": infer_year("\n".join(pages[:2])),
        "arxiv_id": infer_arxiv_id("\n".join(pages[:2])),
        "doi": infer_doi("\n".join(pages[:2])),
        "language": infer_language("\n".join(pages[:2])),
    }
    return metadata, blocks


def infer_year(text: str) -> int | None:
    years = [int(y) for y in re.findall(r"\b(19\d{2}|20\d{2})\b", text)]
    years = [y for y in years if 1990 <= y <= 2035]
    return years[0] if years else None


def infer_arxiv_id(text: str) -> str | None:
    match = re.search(r"arXiv[:\s]*([0-9]{4}\.[0-9]{4,5}(?:v\d+)?)", text, re.I)
    return match.group(1) if match else None


def infer_doi(text: str) -> str | None:
    match = re.search(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b", text)
    return match.group(0) if match else None


def infer_language(text: str) -> str:
    zh = len(re.findall(r"[\u4e00-\u9fff]", text))
    en = len(re.findall(r"[A-Za-z]", text))
    if zh and en:
        return "mixed"
    if zh > en:
        return "zh"
    return "en"
