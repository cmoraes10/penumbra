"""
Shared utilities for the Penumbra pipeline.

Centralises what every collector needs: config loading, an HTTP client with
exponential-backoff retries to survive API instability, disk caching for raw
downloads, and IBGE code normalisation, which is the key that joins all sources.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"
RAW_DATA = ROOT / "data" / "raw"
PROCESSED_DATA = ROOT / "data" / "processed"

# some public servers reject requests without a browser user-agent
HEADERS = {"User-Agent": "Mozilla/5.0 (Penumbra open data pipeline)"}


def load_config(name: str) -> dict:
    """Reads a JSON file from the config directory."""
    with open(CONFIG / name, encoding="utf-8") as f:
        return json.load(f)


def ibge_code(value: Any) -> str:
    """Normalises any municipality code to a seven-digit string.

    The localities API returns the code as an integer, while other sources use
    text. Without this normalisation the cross-source join silently fails.
    """
    return str(value).strip().zfill(7)


def get_json(
    url: str,
    params: dict | None = None,
    retries: int = 4,
    base_wait: float = 1.5,
    timeout: int = 60,
) -> Any:
    """GETs a URL and returns JSON, retrying with exponential backoff on failure.

    Network errors and 429/5xx responses are treated as transient and retried,
    doubling the wait each round. A 404 is permanent and raises immediately.
    """
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
            if response.status_code == 404:
                response.raise_for_status()
            if response.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(f"transient status {response.status_code}")
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(base_wait * (2 ** attempt))
    raise RuntimeError(f"failed to fetch {url}: {last_error}")


def download_file(url: str, dest: Path, force: bool = False, timeout: int = 180) -> Path:
    """Downloads a large file to local cache, reusing it if it already exists."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not force:
        return dest
    with requests.get(url, headers=HEADERS, timeout=timeout, stream=True) as response:
        response.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=1 << 16):
                f.write(chunk)
    return dest


def save_json(data: Any, dest: Path) -> None:
    """Writes JSON with human-readable formatting, preserving accents."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
