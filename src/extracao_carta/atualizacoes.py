"""Histórico de atualizações das cartas ativas (gerenciamento_historicoservico).

Conta só registros aprovados: pendentes e recusados não chegaram ao Portal.
"""
from __future__ import annotations

from .queries import PORTAL_URL_BASE

POR_CARTA = """
    WITH h AS (
        SELECT servico_id,
               max(versao)                                   AS versao,
               count(*) FILTER (WHERE acao = 'Edição')       AS edicoes,
               count(*) FILTER (WHERE acao = 'Revisão')      AS revisoes,
               count(*) FILTER (WHERE acao LIKE '%%etapa')   AS etapas,
               count(*)                                      AS total,
               max(created_at)                               AS ultima
        FROM gerenciamento_historicoservico
        WHERE aprovado
        GROUP BY servico_id
    ), r AS (
        SELECT servico_id, max(data) AS ultima_revisao
        FROM gerenciamento_revisaoservico GROUP BY servico_id
    )
    SELECT COALESCE(o.sigla, ''), s.titulo, COALESCE(tema.slug, ''), s.slug,
           COALESCE(h.versao, 0), COALESCE(h.edicoes, 0), COALESCE(h.revisoes, 0),
           COALESCE(h.etapas, 0), COALESCE(h.total, 0),
           s.created_at::date, h.ultima::date, r.ultima_revisao
    FROM gerenciamento_servicos s
    LEFT JOIN gerenciamento_setor  st   ON s.setor_id = st.id
    LEFT JOIN gerenciamento_orgaos o    ON st.orgao_id = o.id
    LEFT JOIN gerenciamento_temas  tema ON s.tema_id  = tema.id
    LEFT JOIN h ON h.servico_id = s.id
    LEFT JOIN r ON r.servico_id = s.id
    WHERE s.ativo AND s.titulo IS NOT NULL
    ORDER BY 1, 2
"""

POR_ANO = """
    SELECT extract(year FROM h.created_at)::int, h.acao, count(*)
    FROM gerenciamento_historicoservico h
    JOIN gerenciamento_servicos s ON s.id = h.servico_id
    WHERE h.aprovado AND s.ativo AND s.titulo IS NOT NULL
    GROUP BY 1, 2 ORDER BY 1, 2
"""


def por_carta(conn) -> list[tuple]:
    """Uma linha por carta ativa; troca categoria+slug pela URL do Portal."""
    with conn.cursor() as cur:
        cur.execute(POR_CARTA)
        rows = cur.fetchall()
    out = []
    for sigla, titulo, cat, slug, *resto in rows:
        url = f"{PORTAL_URL_BASE}/{cat}/{slug}" if cat and slug else ""
        out.append((sigla, titulo, url, *resto))
    return out


def por_ano(conn) -> list[tuple[int, str, int]]:
    with conn.cursor() as cur:
        cur.execute(POR_ANO)
        return cur.fetchall()
