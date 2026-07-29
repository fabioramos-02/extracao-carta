"""Queries reutilizáveis contra o banco `admin_prd`."""
from __future__ import annotations

import sys

from .html_text import to_text
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


CARTAS_ATIVAS_COM_SETOR = """
    SELECT
        COALESCE(o.sigla, '')   AS sigla_orgao,
        COALESCE(st.nome, '')   AS setor,
        s.titulo                AS titulo_servico,
        COALESCE(tema.slug, '') AS categoria,
        s.slug                  AS slug_servico
    FROM gerenciamento_servicos s
    LEFT JOIN gerenciamento_setor  st   ON s.setor_id = st.id
    LEFT JOIN gerenciamento_orgaos o    ON st.orgao_id = o.id
    LEFT JOIN gerenciamento_temas  tema ON s.tema_id  = tema.id
    WHERE s.ativo = true
      AND s.titulo IS NOT NULL
    ORDER BY sigla_orgao, setor, categoria, titulo_servico
"""


def cartas_ativas_com_setor(conn) -> list[tuple[str, str, str, str, str]]:
    """Retorna (sigla_orgao, setor, titulo_servico, categoria, url)."""
    with conn.cursor() as cur:
        cur.execute(CARTAS_ATIVAS_COM_SETOR)
        rows = cur.fetchall()
    out: list[tuple[str, str, str, str, str]] = []
    for sigla, setor, titulo, categoria, slug in rows:
        url = (
            f"{PORTAL_URL_BASE}/{categoria}/{slug}"
            if categoria and slug
            else ""
        )
        out.append((sigla or "", setor or "", titulo or "", categoria or "", url))
    return out


def titulos_por_categoria(conn, slug: str) -> list[tuple[str, str]]:
    """Lista (titulo, slug_servico) de serviços ativos no tema `slug`."""
    with conn.cursor() as cur:
        cur.execute(TITULOS_POR_CATEGORIA, (slug,))
        return list(cur.fetchall())


CARTAS_SECOES_BRUTAS = """
    SELECT
        COALESCE(o.sigla, '')              AS sigla_orgao,
        s.titulo                           AS titulo_servico,
        COALESCE(tema.slug, '')            AS categoria,
        s.slug                             AS slug_servico,
        COALESCE(s.descricao, '')          AS descricao,
        COALESCE(s.requisitos, '')         AS requisitos,
        COALESCE(s.custo, '')              AS custo,
        COALESCE(s.publico, '')            AS publico,
        COALESCE(array_to_string(s.publico_especifico, ', '), '') AS publico_especifico,
        COALESCE(CAST(s.tempo_total AS TEXT), '') AS tempo_total,
        COALESCE(s.informacoes_extra, '')  AS informacoes_extra
    FROM gerenciamento_servicos s
    LEFT JOIN gerenciamento_setor  st   ON s.setor_id  = st.id
    LEFT JOIN gerenciamento_orgaos o    ON st.orgao_id = o.id
    LEFT JOIN gerenciamento_temas  tema ON s.tema_id   = tema.id
    WHERE s.ativo = true AND s.titulo IS NOT NULL
    ORDER BY sigla_orgao, categoria, titulo_servico
"""

SECOES = (
    "descricao",
    "requisitos",
    "custo",
    "publico",
    "publico_especifico",
    "tempo_total",
    "informacoes_extra",
)


def cartas_secoes_brutas(conn) -> list[tuple]:
    """Retorna todas as cartas ativas com conteúdo HTML de cada seção."""
    with conn.cursor() as cur:
        cur.execute(CARTAS_SECOES_BRUTAS)
        return list(cur.fetchall())


# União de CARTAS_ATIVAS_COM_SETOR (identificação) + CARTAS_SECOES_BRUTAS (conteúdo).
# Query própria em vez de estender CARTAS_SECOES_BRUTAS: extract_cartas_pdf_video.py
# consome aquela tupla por posição.
CARTAS_ATIVAS_ESTRUTURA = """
    SELECT
        COALESCE(o.sigla, '')              AS sigla_orgao,
        COALESCE(st.nome, '')              AS setor,
        s.titulo                           AS titulo_servico,
        COALESCE(tema.slug, '')            AS categoria,
        s.slug                             AS slug_servico,
        COALESCE(s.descricao, '')          AS o_que_e,
        COALESCE(s.requisitos, '')         AS requisitos,
        COALESCE(s.custo, '')              AS custo,
        COALESCE(s.publico, '')            AS publico,
        COALESCE(array_to_string(s.publico_especifico, ', '), '') AS publico_especifico,
        COALESCE(CAST(s.tempo_total AS TEXT), '') AS tempo_total,
        COALESCE(s.informacoes_extra, '')  AS informacoes_extra,
        s.agendavel                        AS agendavel,
        s.digital                          AS digital
    FROM gerenciamento_servicos s
    LEFT JOIN gerenciamento_setor  st   ON s.setor_id  = st.id
    LEFT JOIN gerenciamento_orgaos o    ON st.orgao_id = o.id
    LEFT JOIN gerenciamento_temas  tema ON s.tema_id   = tema.id
    WHERE s.ativo = true
      AND s.titulo IS NOT NULL
    ORDER BY sigla_orgao, setor, categoria, titulo_servico
"""

# Índices (na tupla do SELECT) das colunas que vêm como HTML e precisam virar texto.
_COLUNAS_HTML = (5, 6, 7, 8, 11)
_SIM_NAO = {True: "sim", False: "não", None: ""}


def cartas_ativas_estrutura(conn) -> list[tuple]:
    """Cartas ativas com identificação + seções da carta já em texto plano.

    Colunas: sigla_orgao, setor, titulo_servico, categoria, url, o_que_e,
    requisitos, custo, publico, publico_especifico, tempo_total,
    informacoes_extra, agendavel, digital.
    """
    with conn.cursor() as cur:
        cur.execute(CARTAS_ATIVAS_ESTRUTURA)
        rows = cur.fetchall()

    out: list[tuple] = []
    for row in rows:
        campos = ["" if v is None else v for v in row]
        for i in _COLUNAS_HTML:
            campos[i] = to_text(campos[i])
        categoria, slug = campos[3], campos[4]
        url = f"{PORTAL_URL_BASE}/{categoria}/{slug}" if categoria and slug else ""
        campos[4] = url  # slug_servico dá lugar à URL montada
        campos[12] = _SIM_NAO.get(row[12], "")
        campos[13] = _SIM_NAO.get(row[13], "")
        out.append(tuple(campos))
    return out
