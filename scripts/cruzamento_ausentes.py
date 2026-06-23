"""CLI: cruza planilha de cartas vs banco para uma categoria-alvo.

Para cada nome de carta na planilha (coluna `--lookup-col`), descobre a categoria
no banco (via match em `gerenciamento_servicos.titulo`). Filtra os que pertencem
a `--categoria`. Compara contra o conjunto de serviços ativos no banco com aquela
categoria. Gera 3 arquivos em `--out-dir`:

    ausentes-no-banco.csv  → na planilha, ausentes no banco (essa categoria)
    extras-no-banco.csv    → no banco, ausentes na planilha
    resumo.md              → contagens e contexto

Uso:
    python scripts/cruzamento_ausentes.py \\
        --in demandas/.../input/planilha.xlsx \\
        --categoria financas-e-impostos \\
        --out-dir demandas/.../output/
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from extracao_carta.db import connect, load_env  # noqa: E402
from extracao_carta.normalize import normalize  # noqa: E402
from extracao_carta.queries import (  # noqa: E402
    titulo_to_categoria,
    titulos_por_categoria,
)
from extracao_carta.xlsx_read import read_column  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Cruzamento planilha x banco por categoria.")
    p.add_argument("--env", default=".env")
    p.add_argument("--in", dest="in_path", required=True, type=Path)
    p.add_argument("--categoria", required=True, help="tema.slug alvo, ex: financas-e-impostos")
    p.add_argument("--out-dir", required=True, type=Path)
    p.add_argument("--lookup-col", type=int, default=2)
    p.add_argument(
        "--mode",
        choices=("mapped", "all"),
        default="mapped",
        help="mapped: filtra planilha pela categoria via match no banco; "
        "all: trata toda a planilha como pertencente à categoria-alvo",
    )
    return p.parse_args()


def write_csv(path: Path, rows: list[tuple[str, ...]], header: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(header)
        w.writerows(rows)


def main() -> int:
    args = parse_args()
    load_env(args.env)

    with connect() as conn:
        mapping, _ = titulo_to_categoria(conn)
        banco_rows = titulos_por_categoria(conn, args.categoria)

    nomes_planilha = read_column(args.in_path, col=args.lookup_col)
    planilha: dict[str, str] = {}
    for nome in nomes_planilha:
        key = normalize(nome)
        if args.mode == "all" or mapping.get(key) == args.categoria:
            planilha.setdefault(key, nome)

    banco: dict[str, tuple[str, str]] = {}  # normalize -> (titulo, slug_servico)
    for titulo, slug in banco_rows:
        banco.setdefault(normalize(titulo), (titulo, slug or ""))

    ausentes = sorted(set(planilha) - set(banco))
    extras = sorted(set(banco) - set(planilha))

    out = args.out_dir
    write_csv(
        out / "ausentes-no-banco.csv",
        [(planilha[k],) for k in ausentes],
        ("titulo_planilha",),
    )
    write_csv(
        out / "extras-no-banco.csv",
        [(banco[k][0], banco[k][1]) for k in extras],
        ("titulo_banco", "slug_servico"),
    )

    if args.mode == "all":
        write_csv(
            out / "ausentes-detalhe.csv",
            [(planilha[k], mapping.get(k, "")) for k in ausentes],
            ("titulo_planilha", "categoria_atual_no_banco"),
        )

    resumo = out / "resumo.md"
    resumo.parent.mkdir(parents=True, exist_ok=True)
    resumo.write_text(
        f"# Cruzamento — categoria `{args.categoria}`\n\n"
        f"- Planilha (`{args.in_path.name}`) na categoria: **{len(planilha)}**\n"
        f"- Banco (ativos, tema.slug = `{args.categoria}`): **{len(banco)}**\n"
        f"- Ausentes no banco (planilha − banco): **{len(ausentes)}**\n"
        f"- Extras no banco (banco − planilha): **{len(extras)}**\n",
        encoding="utf-8",
    )

    print(f"[planilha:{args.categoria}] {len(planilha)}")
    print(f"[banco:{args.categoria}]     {len(banco)}")
    print(f"[ausentes_no_banco]          {len(ausentes)}")
    print(f"[extras_no_banco]            {len(extras)}")
    print(f"[ok] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
