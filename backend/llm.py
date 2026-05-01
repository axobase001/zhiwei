from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol

from .config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_PROVIDER


class LLMProvider(Protocol):
    def complete_json(self, system: str, user: str, schema_hint: dict[str, Any]) -> dict[str, Any]:
        ...


@dataclass
class OpenAICompatibleProvider:
    base_url: str
    api_key: str
    model: str

    def complete_json(self, system: str, user: str, schema_hint: dict[str, Any]) -> dict[str, Any]:
        if not self.base_url or not self.api_key or not self.model:
            raise RuntimeError("LLM provider 缺少 ZHIWEI_LLM_BASE_URL / API_KEY / MODEL")
        url = self.base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            timeout = int(os.environ.get("ZHIWEI_LLM_TIMEOUT", "240"))
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.URLError as exc:
            raise RuntimeError(f"LLM 调用失败: {exc}") from exc
        data = json.loads(raw)
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)


def configured_provider() -> LLMProvider | None:
    if LLM_PROVIDER.lower() in {"openai", "openai_compatible", "deepseek", "qwen"}:
        return OpenAICompatibleProvider(LLM_BASE_URL, LLM_API_KEY, LLM_MODEL)
    return None
