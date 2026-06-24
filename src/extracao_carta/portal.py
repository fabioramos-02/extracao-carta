"""Cliente HTTP para a API pública do Portal MS (admin.ms.gov.br/api).

A base e o Api-Key estão hardcoded como defaults porque já são embarcados em
texto claro no bundle JS público de https://www.ms.gov.br (não são segredo).
Podem ser sobrescritos por `PORTAL_MS_API_URL` / `PORTAL_MS_API_KEY` no .env.
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_BASE = "https://admin.ms.gov.br/api"
DEFAULT_KEY = "Api-Key 8tqFBwkS.6eLeClPnZvZEioz7ghV4GuNvvPPf4GMG"
USER_AGENT = "extracao-carta/0.1 (SETDIG)"


def _get(url: str, key: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(
        url, headers={"Authorization": key, "User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_categoria(slug: str, raw_dump: Path | None = None) -> list[dict]:
    """Cartas ativas do Portal MS na categoria `slug` (tema.slug).

    Endpoint: `GET /cms/servicos/?categoria_slug=<slug>&ativo=true&items_size=10000`
    (mesma chamada que a SPA do portal faz para renderizar /categoria/<slug>).

    Retorna lista de dicts com: titulo, slug, categoria_slug, orgao_sigla, url.
    """
    base = os.getenv("PORTAL_MS_API_URL", DEFAULT_BASE).rstrip("/")
    key = os.getenv("PORTAL_MS_API_KEY", DEFAULT_KEY)
    qs = urllib.parse.urlencode(
        {"categoria_slug": slug, "ativo": "true", "page": 1, "items_size": 10000}
    )
    raw = _get(f"{base}/cms/servicos/?{qs}", key)
    if raw_dump is not None:
        raw_dump.parent.mkdir(parents=True, exist_ok=True)
        raw_dump.write_bytes(raw)
    payload = json.loads(raw)
    results = payload.get("results", []) or []
    return [
        {
            "titulo": (r.get("titulo") or "").strip(),
            "slug": r.get("slug") or "",
            "categoria_slug": r.get("categoria_slug") or "",
            "orgao_sigla": r.get("orgao_sigla") or "",
            "url": f"https://www.ms.gov.br/{r.get('categoria_slug', '')}/{r.get('slug', '')}",
        }
        for r in results
    ]
