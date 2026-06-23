"""Queries reutilizáveis contra o banco `admin_prd`."""
from __future__ import annotations

import sys

from .normalize import normalize

TITULO_TEMA = """
    SELECT s.titulo, tema.slug
    FROM gerenciamento_servicos s
    LEFT JOIN gerenciamento_temas tema ON s.tema_id = tema.id
    WHERE s.ativo = true AND s.titulo IS NOT NULL
"""

TITULOS_POR_CATEGORIA = """
    SELECT s.titulo, s.slug
    FROM gerenciamento_servicos s
    JOIN gerenciamento_temas tema ON s.tema_id = tema.id
    WHERE s.ativo = true AND s.titulo IS NOT NULL AND tema.slug = %s
"""


def titulo_to_categoria(conn) -> tuple[dict[str, str], int]:
    """Mapa { normalize(titulo) -> tema.slug } para serviços ativos.

    Em colisão (mesmo título normalizado em temas distintos), usa o primeiro
    e loga warning em stderr. Retorna (mapa, qtd_colisões).
    """
    buckets: dict[str, set[str]] = {}
    with conn.cursor() as cur:
        cur.execute(TITULO_TEMA)
        for titulo, slug in cur.fetchall():
            key = normalize(titulo)
            if not key:
                continue
            buckets.setdefault(key, set()).add(slug or "")

    flat: dict[str, str] = {}
    colisoes = 0
    for key, slugs in buckets.items():
        slugs.discard("")
        if len(slugs) > 1:
            colisoes += 1
            print(
                f"[warn] colisão para '{key}': {sorted(slugs)} — usando o primeiro",
                file=sys.stderr,
            )
        flat[key] = next(iter(slugs), "")
    return flat, colisoes


def titulos_por_categoria(conn, slug: str) -> list[tuple[str, str]]:
    """Lista (titulo, slug_servico) de serviços ativos no tema `slug`."""
    with conn.cursor() as cur:
        cur.execute(TITULOS_POR_CATEGORIA, (slug,))
        return list(cur.fetchall())
