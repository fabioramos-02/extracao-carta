"""CLI: extrai todas as cartas ativas do banco e gera XLSX.

Colunas: siglaorgao | titulo_servico | categoria | url

Uso:
    python scripts/extract_cartas_ativas.py \\
        --out demandas/2026-06/004-cartas-ativas-completo/output/cartas-ativas.xlsx
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from extracao_carta.db import connect, load_env  # noqa: E402
from extracao_carta.queries import cartas_ativas_completas  # noqa: E402

HEADERS = ("siglaorgao", "titulo_servico", "categoria", "url")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Exporta cartas ativas para XLSX.")
    p.add_argument("--env", default=".env")
    p.add_argument("--out", dest="out_path", required=True, type=Path)
    return p.parse_args()


def write_xlsx(path: Path, rows: list[tuple[str, str, str, str]]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "cartas_ativas"
    ws.append(HEADERS)
    for r in rows:
        ws.append(r)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def main() -> int:
    args = parse_args()
    load_env(args.env)
    with connect() as conn:
        rows = cartas_ativas_completas(conn)
    write_xlsx(args.out_path, rows)
    sem_orgao = sum(1 for r in rows if not r[0])
    sem_categoria = sum(1 for r in rows if not r[2])
    print(f"[db] cartas ativas: {len(rows)}")
    print(f"[warn] sem sigla_orgao: {sem_orgao} | sem categoria: {sem_categoria}")
    print(f"[ok] gravado: {args.out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
