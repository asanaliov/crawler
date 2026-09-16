"""Local LLM helper backed by an Ollama server (http://localhost:11434)."""

from __future__ import annotations

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2"
MAX_CHARS = 6000


def summarize(text: str, title: str = "", model: str | None = None, timeout: float = 60.0) -> str:
    """Summarize page text in 1-3 sentences using a local Ollama model.

    Returns an empty string if the local model is unreachable, so the
    crawler still works without a running Ollama server.
    """
    snippet = text[:MAX_CHARS]
    prompt = (
        "Summarize the following web page in 1-3 concise sentences. "
        "Only output the summary, no preamble.\n\n"
        f"Title: {title}\n\nContent: {snippet}"
    )

    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": model or DEFAULT_MODEL, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except requests.RequestException as exc:
        print(f"warning: local model unavailable ({exc})")
        return ""
