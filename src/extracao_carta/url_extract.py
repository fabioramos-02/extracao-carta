"""Extração de URLs de PDF e vídeo de conteúdo HTML."""
from __future__ import annotations

import re

_RE_HREF = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)
_RE_SRC = re.compile(r'src=["\']([^"\']+)["\']', re.IGNORECASE)

_PDF_SUFFIX = re.compile(r'\.pdf(\?[^"\']*)?$', re.IGNORECASE)
_VIDEO_HOST = re.compile(
    r'(youtube\.com|youtu\.be|vimeo\.com)', re.IGNORECASE
)


def _classify(url: str) -> str | None:
    if _PDF_SUFFIX.search(url):
        return "pdf"
    if _VIDEO_HOST.search(url):
        return "video"
    return None


def extract_urls(html: str) -> list[dict[str, str]]:
    """Retorna lista de {"tipo": "pdf"|"video", "url": "..."} extraída do HTML."""
    if not html:
        return []

    found: list[dict[str, str]] = []
    seen: set[str] = set()

    candidates = _RE_HREF.findall(html) + _RE_SRC.findall(html)
    for url in candidates:
        url = url.strip()
        if not url or url in seen:
            continue
        tipo = _classify(url)
        if tipo:
            seen.add(url)
            found.append({"tipo": tipo, "url": url})

    return found
