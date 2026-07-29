"""CLI: cartas de serviço ativas com identificação + seções da carta, em XLSX.

Colunas: orgao_sigla | setor | titulo_servico | categoria | url | o_que_e |
requisitos | custo | publico | publico_especifico | tempo_total |
informacoes_extra | agendavel | digital
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from extracao_carta.db import connect, load_env  # noqa: E402
from extracao_carta.queries import cartas_ativas_estrutura  # noqa: E402

HEADERS = (
    "orgao_sigla", "setor", "titulo_servico", "categoria", "url",
    "o_que_e", "requisitos", "custo", "publico", "publico_especifico",
    "tempo_total", "informacoes_extra", "agendavel", "digital",
)

# Larguras por coluna: identificação estreita, seções de conteúdo largas.
LARGURAS = (14, 34, 52, 30, 60, 60, 60, 24, 30, 30, 12, 60, 11, 9)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Exporta cartas de serviço ativas com as seções da carta para XLSX."
    )
    p.add_argument("--env", default=".env")
    p.add_argument("--out", dest="out_path", required=True, type=Path)
    return p.parse_args()


def write_xlsx(path: Path, rows: list[tuple]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "cartas_ativas"
    ws.append(HEADERS)
    for r in rows:
        ws.append(r)

    for i, largura in enumerate(LARGURAS, start=1):
        ws.column_dimensions[get_column_letter(i)].width = largura
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(vertical="center")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def main() -> int:
    args = parse_args()
    load_env(args.env)
    with connect() as conn:
        rows = cartas_ativas_estrutura(conn)
    write_xlsx(args.out_path, rows)

    orgaos = len({r[0] for r in rows if r[0]})
    categorias = len({r[3] for r in rows if r[3]})
    sem_categoria = sum(1 for r in rows if not r[3])
    print(f"[db] cartas ativas: {len(rows)}")
    print(f"[db] orgaos: {orgaos} | categorias: {categorias}")
    if sem_categoria:
        print(f"[warn] sem categoria: {sem_categoria}")
    print(f"[ok] gravado: {args.out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
