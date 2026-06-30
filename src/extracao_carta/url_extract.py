"""Extração de URLs de documentos e mídia de conteúdo HTML."""
from __future__ import annotations

import re

_RE_HREF = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)
_RE_SRC  = re.compile(r'src=["\']([^"\']+)["\']',  re.IGNORECASE)

_DOC_SUFFIX   = re.compile(r'\.(docx?)(\?[^"\']*)?$', re.IGNORECASE)
_PDF_SUFFIX   = re.compile(r'\.pdf(\?[^"\']*)?$',     re.IGNORECASE)
_MP4_SUFFIX   = re.compile(r'\.mp4(\?[^"\']*)?$',     re.IGNORECASE)
_VIDEO_HOST   = re.compile(r'(youtube\.com|youtu\.be|vimeo\.com)', re.IGNORECASE)


def _classify(url: str) -> str | None:
    if _PDF_SUFFIX.search(url):
        return "pdf"
    if _DOC_SUFFIX.search(url):
        return "doc"
    if _MP4_SUFFIX.search(url) or _VIDEO_HOST.search(url):
        return "video"
    return None


def extract_urls(html: str) -> list[dict[str, str]]:
    """Retorna lista de {"tipo": "pdf"|"doc"|"video", "url": "..."} extraída do HTML."""
    if not html:
        return []

    found: list[dict[str, str]] = []
    seen: set[str] = set()

    for url in _RE_HREF.findall(html) + _RE_SRC.findall(html):
        url = url.strip()
        if not url or url in seen:
            continue
        tipo = _classify(url)
        if tipo:
            seen.add(url)
            found.append({"tipo": tipo, "url": url})

    return found
