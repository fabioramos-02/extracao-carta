"""CLI: histórico de atualizações das cartas ativas em XLSX (abas resumo, por_carta, por_ano).

Uso:
    python scripts/extract_atualizacoes_cartas.py \\
        --out demandas/2026-11/002-atualizacoes-cartas/output/atualizacoes-cartas.xlsx
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from extracao_carta.atualizacoes import por_ano, por_carta  # noqa: E402
from extracao_carta.db import connect, load_env  # noqa: E402

CARTA_HEADERS = ("orgao", "titulo_servico", "url_portal", "versao_atual", "edicoes",
                 "revisoes", "alteracoes_etapas", "total_alteracoes", "criada_em",
                 "ultima_alteracao", "ultima_revisao")


def resumo(cartas: list[tuple], anos: list[tuple]) -> list[tuple]:
    hoje = date.today()
    total = sum(c[7] for c in cartas)
    alt_2026 = sum(1 for c in cartas if c[9] and c[9].year == hoje.year)
    alt_12m = sum(1 for c in cartas if c[9] and c[9] >= hoje - timedelta(days=365))
    rev_12m = sum(1 for c in cartas if c[10] and c[10] >= hoje - timedelta(days=365))
    por_acao: dict[str, int] = defaultdict(int)
    for _, acao, n in anos:
        por_acao[acao] += n
    linhas = [
        ("Data da extração", hoje.strftime("%d/%m/%Y")),
        ("Cartas ativas no Portal", len(cartas)),
        ("Alterações aprovadas (todo o histórico)", total),
        (f"Cartas alteradas em {hoje.year}", alt_2026),
        ("Cartas alteradas nos últimos 12 meses", alt_12m),
        ("Cartas revisadas nos últimos 12 meses", rev_12m),
        ("Maior número de versão de uma carta", max((c[3] for c in cartas), default=0)),
        ("", ""),
        ("Alterações por tipo", ""),
    ]
    linhas += sorted(por_acao.items(), key=lambda x: -x[1])
    return linhas


def aba(wb: Workbook, titulo: str, headers: tuple, rows) -> None:
    ws = wb.create_sheet(titulo)
    ws.append(headers)
    for c in ws[1]:
        c.font = Font(bold=True)
    for r in rows:
        ws.append(list(r))
    ws.freeze_panes = "A2"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--env", default=".env")
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    load_env(args.env)
    with connect() as conn:
        cartas, anos = por_carta(conn), por_ano(conn)

    acoes = sorted({a for _, a, _ in anos})
    grade: dict[int, dict[str, int]] = defaultdict(dict)
    for ano, acao, n in anos:
        grade[ano][acao] = n
    linhas_ano = [(ano, *(g.get(a, 0) for a in acoes), sum(g.values()))
                  for ano, g in sorted(grade.items())]

    wb = Workbook()
    wb.remove(wb.active)
    aba(wb, "resumo", ("indicador", "valor"), resumo(cartas, anos))
    aba(wb, "por_carta", CARTA_HEADERS, cartas)
    aba(wb, "por_ano", ("ano", *acoes, "total"), linhas_ano)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(args.out)
    for k, v in resumo(cartas, anos)[:7]:
        print(f"{k}: {v}")
    print(f"[ok] gravado: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
