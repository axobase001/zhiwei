from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"
DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "zhiwei.db"
STATIC_DIR = PROJECT_ROOT / "static"
SAMPLES_DIR = PROJECT_ROOT / "samples"


def load_dotenv(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().lstrip("\ufeff")
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_dotenv()

APP_HOST = os.environ.get("ZHIWEI_HOST", "127.0.0.1")
APP_PORT = int(os.environ.get("ZHIWEI_PORT", "8765"))

_openai_key = os.environ.get("OPENAI_API_KEY", "")
_openai_base = os.environ.get("OPENAI_BASE_URL", "")
_openai_model = os.environ.get("OPENAI_MODEL", "")

LLM_PROVIDER = os.environ.get(
    "ZHIWEI_LLM_PROVIDER",
    "openai_compatible" if (_openai_key and _openai_base and _openai_model) else "heuristic",
)
LLM_BASE_URL = os.environ.get("ZHIWEI_LLM_BASE_URL") or _openai_base
LLM_API_KEY = os.environ.get("ZHIWEI_LLM_API_KEY") or _openai_key
LLM_MODEL = os.environ.get("ZHIWEI_LLM_MODEL") or _openai_model


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
