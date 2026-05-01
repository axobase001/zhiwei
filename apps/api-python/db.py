from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .config import DB_PATH, ensure_dirs
from .utils import json_dumps, now_iso


SCHEMA_SQL = """
create table if not exists papers (
  id text primary key,
  title text not null,
  authors text not null default '[]',
  year integer,
  venue text,
  arxiv_id text,
  doi text,
  language text not null default 'en',
  file_path text not null,
  status text not null,
  created_at text not null,
  updated_at text not null
);

create table if not exists document_blocks (
  id text primary key,
  paper_id text not null,
  block_type text not null,
  content text not null,
  page integer not null,
  section text,
  bbox_json text,
  anchor_id text not null,
  created_at text not null,
  foreign key (paper_id) references papers(id) on delete cascade
);

create table if not exists anchors (
  id text primary key,
  paper_id text not null,
  page integer not null,
  section text,
  block_id text not null,
  bbox_json text,
  text_span text not null,
  source_type text not null,
  foreign key (paper_id) references papers(id) on delete cascade
);

create table if not exists paper_ir (
  id text primary key,
  paper_id text not null,
  ir_json text not null,
  version integer not null,
  created_at text not null,
  foreign key (paper_id) references papers(id) on delete cascade
);

create table if not exists user_corrections (
  id text primary key,
  paper_id text not null,
  target_type text not null,
  target_id text not null,
  old_value text,
  new_value text not null,
  created_at text not null,
  foreign key (paper_id) references papers(id) on delete cascade
);

create table if not exists processing_logs (
  id text primary key,
  paper_id text not null,
  step text not null,
  status text not null,
  message text not null,
  created_at text not null,
  foreign key (paper_id) references papers(id) on delete cascade
);
"""


def connect() -> sqlite3.Connection:
    ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("pragma foreign_keys=on")
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA_SQL)


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)


def log(conn: sqlite3.Connection, paper_id: str, step: str, status: str, message: str) -> None:
    conn.execute(
        "insert into processing_logs (id,paper_id,step,status,message,created_at) values (?,?,?,?,?,?)",
        (f"log_{paper_id}_{step}_{now_iso()}", paper_id, step, status, message, now_iso()),
    )


def list_papers() -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            "select * from papers order by created_at desc"
        ).fetchall()
    return [dict(row) | {"authors": json.loads(row["authors"] or "[]")} for row in rows]


def get_paper(paper_id: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute("select * from papers where id=?", (paper_id,)).fetchone()
    item = row_to_dict(row)
    if item:
        item["authors"] = json.loads(item.get("authors") or "[]")
    return item


def get_blocks(paper_id: str) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            "select * from document_blocks where paper_id=? order by page, id",
            (paper_id,),
        ).fetchall()
    blocks = []
    for row in rows:
        item = dict(row)
        item["bbox"] = json.loads(item.pop("bbox_json") or "null")
        blocks.append(item)
    return blocks


def get_anchors(paper_id: str) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            "select * from anchors where paper_id=? order by page, id",
            (paper_id,),
        ).fetchall()
    anchors = []
    for row in rows:
        item = dict(row)
        item["bbox"] = json.loads(item.pop("bbox_json") or "null")
        anchors.append(item)
    return anchors


def get_latest_ir(paper_id: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            "select * from paper_ir where paper_id=? order by version desc limit 1",
            (paper_id,),
        ).fetchone()
    if not row:
        return None
    return json.loads(row["ir_json"])


def save_ir(conn: sqlite3.Connection, paper_id: str, ir: dict[str, Any]) -> None:
    row = conn.execute(
        "select coalesce(max(version), 0) as v from paper_ir where paper_id=?",
        (paper_id,),
    ).fetchone()
    version = int(row["v"] or 0) + 1
    conn.execute(
        "insert into paper_ir (id,paper_id,ir_json,version,created_at) values (?,?,?,?,?)",
        (f"ir_{paper_id}_{version}", paper_id, json_dumps(ir), version, now_iso()),
    )


def delete_paper(paper_id: str) -> None:
    with connect() as conn:
        paper = conn.execute("select file_path from papers where id=?", (paper_id,)).fetchone()
        conn.execute("delete from papers where id=?", (paper_id,))
    if paper:
        path = Path(paper["file_path"])
        if path.exists():
            try:
                path.unlink()
            except OSError:
                pass
