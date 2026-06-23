"""CLI: enriquece planilha SEFAZ com `tema.slug` por linha.

Uso:
    python scripts/enrich_categorias.py \\
        --in  demandas/2026-06/001-categorias-sefaz/input/Cópia\\ de\\ Categorias\\ SEFAZ.xlsx \\
        --out demandas/2026-06/001-categorias-sefaz/output/categorias-sefaz-enriched.xlsx
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# permite rodar sem instalar como pacote
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from extracao_carta.db import connect, load_env  # noqa: E402
from extracao_carta.queries import titulo_to_categoria  # noqa: E402
from extracao_carta.xlsx import enrich_column  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Enriquece planilha com categoria do serviço.")
    p.add_argument("--env", default=".env")
    p.add_argument("--in", dest="in_path", required=True, type=Path)
    p.add_argument("--out", dest="out_path", required=True, type=Path)
    p.add_argument("--lookup-col", type=int, default=2, help="coluna do nome do serviço (1-based)")
    p.add_argument("--write-col", type=int, default=3, help="coluna onde gravar a categoria")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    load_env(args.env)
    with connect() as conn:
        mapping, colisoes = titulo_to_categoria(conn)
    print(f"[db] títulos únicos: {len(mapping)} | colisões: {colisoes}")

    total, casados = enrich_column(
        args.in_path,
        args.out_path,
        mapping,
        lookup_col=args.lookup_col,
        write_col=args.write_col,
    )
    print(f"[xlsx] total: {total} | casados: {casados} | sem match: {total - casados}")
    print(f"[ok] gravado: {args.out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
