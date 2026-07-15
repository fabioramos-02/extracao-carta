"""CLI: cartas ativas + setor do órgão em XLSX.

Colunas: siglaorgao | setor | titulo_servico | categoria | url
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from extracao_carta.db import connect, load_env  # noqa: E402
from extracao_carta.queries import cartas_ativas_com_setor  # noqa: E402

HEADERS = ("siglaorgao", "setor", "titulo_servico", "categoria", "url")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Exporta cartas ativas + setor para XLSX.")
    p.add_argument("--env", default=".env")
    p.add_argument("--out", dest="out_path", required=True, type=Path)
    return p.parse_args()


def write_xlsx(path: Path, rows: list[tuple[str, str, str, str, str]]) -> None:
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
        rows = cartas_ativas_com_setor(conn)
    write_xlsx(args.out_path, rows)
    sem_orgao = sum(1 for r in rows if not r[0])
    sem_setor = sum(1 for r in rows if not r[1])
    sem_categoria = sum(1 for r in rows if not r[3])
    print(f"[db] cartas ativas: {len(rows)}")
    print(
        f"[warn] sem sigla_orgao: {sem_orgao} | sem setor: {sem_setor} | "
        f"sem categoria: {sem_categoria}"
    )
    print(f"[ok] gravado: {args.out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
