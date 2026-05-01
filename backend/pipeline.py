from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from .config import UPLOAD_DIR
from .db import connect, log, save_ir
from .extractor import generate_paper_ir
from .parser import DocumentBlock, parse_pdf
from .utils import json_dumps, new_id, now_iso
from .verifier import verify_ir


def import_pdf(src_path: Path, original_name: str) -> str:
    paper_id = new_id("paper")
    target = UPLOAD_DIR / f"{paper_id}.pdf"
    shutil.copyfile(src_path, target)
    return process_pdf(paper_id, target, original_name, create=True)


def process_pdf(paper_id: str, pdf_path: Path, original_name: str | None = None, create: bool = False) -> str:
    metadata, blocks = parse_pdf(pdf_path, paper_id)
    metadata["uploaded_at"] = now_iso()
    with connect() as conn:
        if create:
            conn.execute(
                """insert into papers
                (id,title,authors,year,venue,arxiv_id,doi,language,file_path,status,created_at,updated_at)
                values (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    paper_id,
                    metadata.get("title") or original_name or "未命名论文",
                    json_dumps(metadata.get("authors", [])),
                    metadata.get("year"),
                    metadata.get("venue"),
                    metadata.get("arxiv_id"),
                    metadata.get("doi"),
                    metadata.get("language", "en"),
                    str(pdf_path),
                    "processing",
                    now_iso(),
                    now_iso(),
                ),
            )
        else:
            conn.execute("delete from document_blocks where paper_id=?", (paper_id,))
            conn.execute("delete from anchors where paper_id=?", (paper_id,))
            conn.execute("update papers set status=?, updated_at=? where id=?", ("processing", now_iso(), paper_id))
        log(conn, paper_id, "pdf_parsing", "ok", f"Parsed {len(blocks)} document blocks.")
        insert_blocks(conn, paper_id, blocks)
        ir = generate_paper_ir(metadata, blocks)
        ir["verification"] = verify_ir(ir)
        save_ir(conn, paper_id, ir)
        conn.execute(
            """update papers set title=?, authors=?, year=?, venue=?, arxiv_id=?, doi=?, language=?, status=?, updated_at=?
               where id=?""",
            (
                metadata.get("title") or original_name or "未命名论文",
                json_dumps(metadata.get("authors", [])),
                metadata.get("year"),
                metadata.get("venue"),
                metadata.get("arxiv_id"),
                metadata.get("doi"),
                metadata.get("language", "en"),
                "ready" if ir["verification"]["status"] in {"passed", "warning"} else "warning",
                now_iso(),
                paper_id,
            ),
        )
        log(conn, paper_id, "paper_ir_generation", "ok", f"Generated Paper IR with {ir['verification']['anchor_count']} anchors.")
    return paper_id


def insert_blocks(conn: Any, paper_id: str, blocks: list[DocumentBlock]) -> None:
    for block in blocks:
        conn.execute(
            """insert into document_blocks
            (id,paper_id,block_type,content,page,section,bbox_json,anchor_id,created_at)
            values (?,?,?,?,?,?,?,?,?)""",
            (
                block.block_id,
                paper_id,
                block.type,
                block.content,
                block.page,
                block.section,
                json.dumps(block.bbox, ensure_ascii=False) if block.bbox else None,
                block.anchor_id,
                now_iso(),
            ),
        )
        conn.execute(
            """insert into anchors
            (id,paper_id,page,section,block_id,bbox_json,text_span,source_type)
            values (?,?,?,?,?,?,?,?)""",
            (
                block.anchor_id,
                paper_id,
                block.page,
                block.section,
                block.block_id,
                json.dumps(block.bbox, ensure_ascii=False) if block.bbox else None,
                block.content[:1200],
                block.type if block.type in {"formula", "caption", "reference"} else "paragraph",
            ),
        )
