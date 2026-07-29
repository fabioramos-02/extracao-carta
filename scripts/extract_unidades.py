"""CLI: unidades de todos os órgãos, em XLSX com auto_filter.

Colunas: sigla_orgao | nome_orgao | slug_unidade | nome_unidade |
endereco | complemento | bairro | cep | cidade | estado | ativo |
source | identificador_externo | created_at | updated_at

O `auto_filter` deixa filtrar por qualquer coluna direto no Excel —
tipicamente sigla_orgao, cidade, estado ou ativo.
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
from extracao_carta.queries import unidades_com_orgao  # noqa: E402

HEADERS = (
    "sigla_orgao", "nome_orgao",
    "slug_unidade", "nome_unidade",
    "endereco", "complemento", "bairro", "cep",
    "cidade", "estado",
    "ativo",
    "horario_funcionamento", "qtd_servicos",
    "source", "identificador_externo",
    "created_at", "updated_at",
)

LARGURAS = (
    14, 48,
    36, 50,
    48, 28, 24, 12,
    22, 8,
    8,
    60, 12,
    30, 22,
    22, 22,
)

_SIM_NAO = {True: "sim", False: "não", None: ""}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Exporta unidades de todos os órgãos (Carta de Serviços) para XLSX."
    )
    p.add_argument("--env", default=".env")
    p.add_argument("--out", dest="out_path", required=True, type=Path)
    return p.parse_args()


def to_row(r: tuple) -> tuple:
    campos = list(r)
    campos[10] = _SIM_NAO.get(r[10], "")
    campos[15] = r[15].strftime("%Y-%m-%d %H:%M:%S") if r[15] else ""
    campos[16] = r[16].strftime("%Y-%m-%d %H:%M:%S") if r[16] else ""
    return tuple(campos)


def write_xlsx(path: Path, rows: list[tuple]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "unidades"
    ws.append(HEADERS)
    for r in rows:
        ws.append(to_row(r))

    for i, largura in enumerate(LARGURAS, start=1):
        ws.column_dimensions[get_column_letter(i)].width = largura
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(vertical="center")
    ws.freeze_panes = "C2"  # trava sigla_orgao + nome_orgao ao rolar
    ws.auto_filter.ref = ws.dimensions

    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def main() -> int:
    args = parse_args()
    load_env(args.env)
    with connect() as conn:
        rows = unidades_com_orgao(conn)
    write_xlsx(args.out_path, rows)

    orgaos = len({r[0] for r in rows if r[0]})
    cidades = len({r[8] for r in rows if r[8]})
    ativas = sum(1 for r in rows if r[10] is True)
    inativas = sum(1 for r in rows if r[10] is False)
    print(f"[db] unidades: {len(rows)} (ativas={ativas}, inativas={inativas})")
    print(f"[db] orgaos: {orgaos} | cidades: {cidades}")
    print(f"[ok] gravado: {args.out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
