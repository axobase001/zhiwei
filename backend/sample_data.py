from __future__ import annotations

import json

from .config import SAMPLES_DIR
from .db import connect, get_paper, save_ir
from .utils import json_dumps, now_iso


DEMO_ID = "paper_demo_attention"


def _load_demo_ir() -> dict:
    path = SAMPLES_DIR / "attention_demo_ir.json"
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_demo() -> None:
    if get_paper(DEMO_ID):
        return

    ir = _load_demo_ir()
    meta = ir["metadata"]
    anchors = ir.get("anchors", [])

    with connect() as conn:
        conn.execute(
            """insert into papers
            (id,title,authors,year,venue,arxiv_id,doi,language,file_path,status,created_at,updated_at)
            values (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                DEMO_ID,
                meta.get("title", "Attention Is All You Need"),
                json_dumps(meta.get("authors", [])),
                meta.get("year"),
                meta.get("venue"),
                meta.get("arxiv_id"),
                meta.get("doi"),
                meta.get("language", "en"),
                "",
                "示例论文",
                meta.get("uploaded_at") or now_iso(),
                ir.get("generated_at") or now_iso(),
            ),
        )
        for i, anchor in enumerate(anchors, start=1):
            block_id = f"attn_blk_{i:03d}"
            conn.execute(
                """insert into document_blocks
                (id,paper_id,block_type,content,page,section,bbox_json,anchor_id,created_at)
                values (?,?,?,?,?,?,?,?,?)""",
                (
                    block_id,
                    DEMO_ID,
                    anchor.get("source_type", "paragraph"),
                    anchor.get("text_span", ""),
                    anchor.get("page", 1),
                    anchor.get("section"),
                    json_dumps(anchor.get("bbox")) if anchor.get("bbox") else None,
                    anchor["anchor_id"],
                    now_iso(),
                ),
            )
            conn.execute(
                """insert into anchors
                (id,paper_id,page,section,block_id,bbox_json,text_span,source_type)
                values (?,?,?,?,?,?,?,?)""",
                (
                    anchor["anchor_id"],
                    DEMO_ID,
                    anchor.get("page", 1),
                    anchor.get("section"),
                    block_id,
                    json_dumps(anchor.get("bbox")) if anchor.get("bbox") else None,
                    anchor.get("text_span", ""),
                    anchor.get("source_type", "paragraph"),
                ),
            )
        save_ir(conn, DEMO_ID, ir)
