from __future__ import annotations

import cgi
import json
import mimetypes
import os
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from .config import APP_HOST, APP_PORT, STATIC_DIR, ensure_dirs
from .db import connect, delete_paper, get_anchors, get_blocks, get_latest_ir, get_paper, init_db, list_papers
from .exporters import ir_to_markdown
from .pipeline import import_pdf, process_pdf
from .sample_data import ensure_demo
from .utils import json_dumps, new_id, now_iso


class ZhiweiHandler(BaseHTTPRequestHandler):
    server_version = "Zhiwei/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/":
            return self._serve_static("index.html")
        if path.startswith("/static/"):
            return self._serve_static(path.removeprefix("/static/"))
        if path == "/api/health":
            return self._json({"ok": True, "name": "知微", "time": now_iso()})
        if path == "/api/papers":
            return self._json({"papers": list_papers()})
        parts = split_api(path)
        if len(parts) >= 2 and parts[0] == "papers":
            paper_id = parts[1]
            if len(parts) == 2:
                paper = get_paper(paper_id)
                return self._json_or_404(paper)
            if len(parts) == 3 and parts[2] == "blocks":
                return self._json({"blocks": get_blocks(paper_id)})
            if len(parts) == 3 and parts[2] == "anchors":
                return self._json({"anchors": get_anchors(paper_id)})
            if len(parts) == 3 and parts[2] == "ir":
                return self._json_or_404(get_latest_ir(paper_id))
            if len(parts) == 3 and parts[2] == "pdf":
                return self._serve_pdf(paper_id)
            if len(parts) == 4 and parts[2] == "export":
                return self._export(paper_id, parts[3])
        self._not_found()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/api/papers":
            return self._handle_upload()
        parts = split_api(path)
        if len(parts) == 3 and parts[0] == "papers" and parts[2] == "reparse":
            paper = get_paper(parts[1])
            if not paper:
                return self._not_found()
            paper_id = process_pdf(parts[1], Path(paper["file_path"]), None, create=False)
            return self._json({"paper_id": paper_id, "status": "ready"})
        if len(parts) == 3 and parts[0] == "papers" and parts[2] == "corrections":
            return self._handle_correction(parts[1])
        self._not_found()

    def do_DELETE(self) -> None:
        parts = split_api(urlparse(self.path).path)
        if len(parts) == 2 and parts[0] == "papers":
            delete_paper(parts[1])
            return self._json({"ok": True})
        self._not_found()

    def log_message(self, fmt: str, *args: object) -> None:
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def _handle_upload(self) -> None:
        ctype, pdict = cgi.parse_header(self.headers.get("content-type", ""))
        if ctype != "multipart/form-data":
            return self._json({"error": "expected multipart/form-data"}, status=400)
        pdict["boundary"] = bytes(pdict["boundary"], "utf-8")
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": self.headers.get("content-type")})
        fileitem = form["pdf"] if "pdf" in form else None
        if fileitem is None or not getattr(fileitem, "filename", None):
            return self._json({"error": "missing pdf field"}, status=400)
        suffix = Path(fileitem.filename).suffix.lower()
        if suffix != ".pdf":
            return self._json({"error": "only PDF is supported"}, status=400)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(fileitem.file.read())
            tmp_path = Path(tmp.name)
        try:
            paper_id = import_pdf(tmp_path, fileitem.filename)
        finally:
            try:
                tmp_path.unlink()
            except OSError:
                pass
        return self._json({"paper_id": paper_id, "paper": get_paper(paper_id), "ir": get_latest_ir(paper_id)})

    def _handle_correction(self, paper_id: str) -> None:
        paper = get_paper(paper_id)
        if not paper:
            return self._not_found()
        length = int(self.headers.get("content-length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        payload = json.loads(raw)
        correction_id = new_id("corr")
        with connect() as conn:
            conn.execute(
                """insert into user_corrections
                (id,paper_id,target_type,target_id,old_value,new_value,created_at)
                values (?,?,?,?,?,?,?)""",
                (
                    correction_id,
                    paper_id,
                    payload.get("target_type", "unknown"),
                    payload.get("target_id", "unknown"),
                    payload.get("old_value"),
                    json_dumps(payload.get("new_value", payload)),
                    now_iso(),
                ),
            )
        return self._json({"ok": True, "correction_id": correction_id})

    def _serve_pdf(self, paper_id: str) -> None:
        paper = get_paper(paper_id)
        if not paper or not paper.get("file_path"):
            return self._not_found()
        path = Path(paper["file_path"])
        if not path.exists():
            return self._not_found()
        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Length", str(path.stat().st_size))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        with open(path, "rb") as handle:
            self.wfile.write(handle.read())

    def _export(self, paper_id: str, kind: str) -> None:
        ir = get_latest_ir(paper_id)
        if not ir:
            return self._not_found()
        if kind == "json":
            return self._download(json_dumps(ir).encode("utf-8"), f"{paper_id}_paper_ir.json", "application/json; charset=utf-8")
        if kind == "markdown":
            return self._download(ir_to_markdown(ir).encode("utf-8"), f"{paper_id}_notes.md", "text/markdown; charset=utf-8")
        return self._json({"error": "unsupported export"}, status=400)

    def _serve_static(self, rel: str) -> None:
        rel = unquote(rel).replace("\\", "/").lstrip("/")
        path = (STATIC_DIR / rel).resolve()
        if not str(path).startswith(str(STATIC_DIR.resolve())) or not path.exists() or path.is_dir():
            return self._not_found()
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _download(self, data: bytes, filename: str, content_type: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json_or_404(self, payload: object | None) -> None:
        if payload is None:
            return self._not_found()
        self._json(payload)

    def _json(self, payload: object, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _not_found(self) -> None:
        self._json({"error": "not found"}, status=404)


def split_api(path: str) -> list[str]:
    if not path.startswith("/api/"):
        return []
    return [part for part in path.removeprefix("/api/").split("/") if part]


def main() -> None:
    ensure_dirs()
    init_db()
    ensure_demo()
    httpd = ThreadingHTTPServer((APP_HOST, APP_PORT), ZhiweiHandler)
    print(f"知微 running at http://{APP_HOST}:{APP_PORT}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
