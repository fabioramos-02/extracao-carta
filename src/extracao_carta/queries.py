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


CARTAS_ATIVAS_COMPLETAS = """
    SELECT
        COALESCE(o.sigla, '')   AS sigla_orgao,
        s.titulo                AS titulo_servico,
        COALESCE(tema.slug, '') AS categoria,
        s.slug                  AS slug_servico
    FROM gerenciamento_servicos s
    LEFT JOIN gerenciamento_setor  st   ON s.setor_id = st.id
    LEFT JOIN gerenciamento_orgaos o    ON st.orgao_id = o.id
    LEFT JOIN gerenciamento_temas  tema ON s.tema_id  = tema.id
    WHERE s.ativo = true
      AND s.titulo IS NOT NULL
    ORDER BY sigla_orgao, categoria, titulo_servico
"""

CARTAS_ATIVAS_COM_DESCRICAO = """
    SELECT
        COALESCE(o.sigla, '')      AS sigla_orgao,
        s.titulo                   AS titulo_servico,
        COALESCE(tema.slug, '')    AS categoria,
        s.slug                     AS slug_servico,
        COALESCE(s.descricao, '')  AS o_que_e_servico
    FROM gerenciamento_servicos s
    LEFT JOIN gerenciamento_setor  st   ON s.setor_id = st.id
    LEFT JOIN gerenciamento_orgaos o    ON st.orgao_id = o.id
    LEFT JOIN gerenciamento_temas  tema ON s.tema_id  = tema.id
    WHERE s.ativo = true
      AND s.titulo IS NOT NULL
    ORDER BY sigla_orgao, categoria, titulo_servico
"""

PORTAL_URL_BASE = "https://www.ms.gov.br"


def cartas_ativas_completas(conn) -> list[tuple[str, str, str, str]]:
    """Retorna (sigla_orgao, titulo_servico, categoria, url) de todas as cartas ativas."""
    with conn.cursor() as cur:
        cur.execute(CARTAS_ATIVAS_COMPLETAS)
        rows = cur.fetchall()
    out: list[tuple[str, str, str, str]] = []
    for sigla, titulo, categoria, slug in rows:
        url = (
            f"{PORTAL_URL_BASE}/{categoria}/{slug}"
            if categoria and slug
            else ""
        )
        out.append((sigla or "", titulo or "", categoria or "", url))
    return out


def cartas_ativas_com_descricao(
    conn,
) -> list[tuple[str, str, str, str, str]]:
    """Retorna (sigla_orgao, titulo_servico, categoria, url, o_que_e_servico)."""
    with conn.cursor() as cur:
        cur.execute(CARTAS_ATIVAS_COM_DESCRICAO)
        rows = cur.fetchall()
    out: list[tuple[str, str, str, str, str]] = []
    for sigla, titulo, categoria, slug, descricao in rows:
        url = (
            f"{PORTAL_URL_BASE}/{categoria}/{slug}"
            if categoria and slug
            else ""
        )
        out.append((sigla or "", titulo or "", categoria or "", url, descricao or ""))
    return out


def titulos_por_categoria(conn, slug: str) -> list[tuple[str, str]]:
    """Lista (titulo, slug_servico) de serviços ativos no tema `slug`."""
    with conn.cursor() as cur:
        cur.execute(TITULOS_POR_CATEGORIA, (slug,))
        return list(cur.fetchall())
