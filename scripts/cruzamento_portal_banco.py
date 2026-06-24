"""CLI: compara cartas ativas do Portal MS x banco `admin_prd` na categoria-alvo.

Gera em `--out-dir`:

    portal_so.csv → cartas no portal sem match no banco (titulo, url)
    banco_so.csv  → cartas no banco sem match no portal (titulo, slug_servico)
    resumo.md     → contagens

Uso:
    python scripts/cruzamento_portal_banco.py \\
        --categoria financas-e-impostos \\
        --out-dir demandas/.../output
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
from extracao_carta.portal import fetch_categoria  # noqa: E402
from extracao_carta.queries import titulos_por_categoria  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Portal MS x banco por categoria.")
    p.add_argument("--env", default=".env")
    p.add_argument("--categoria", required=True, help="tema.slug alvo")
    p.add_argument("--out-dir", required=True, type=Path)
    p.add_argument(
        "--raw-dump",
        type=Path,
        default=None,
        help="Caminho para salvar JSON bruto. Default: <out-dir>/../input/portal.json",
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

    raw = args.raw_dump or (args.out_dir.parent / "input" / "portal.json")
    portal_items = fetch_categoria(args.categoria, raw_dump=raw)

    with connect() as conn:
        banco_rows = titulos_por_categoria(conn, args.categoria)

    portal: dict[str, dict] = {}
    for it in portal_items:
        portal.setdefault(normalize(it["titulo"]), it)

    banco: dict[str, tuple[str, str]] = {}
    for titulo, slug in banco_rows:
        banco.setdefault(normalize(titulo), (titulo, slug or ""))

    so_portal = sorted(set(portal) - set(banco))
    so_banco = sorted(set(banco) - set(portal))
    intersec = len(set(portal) & set(banco))

    out = args.out_dir
    write_csv(
        out / "portal_so.csv",
        [(portal[k]["titulo"], portal[k]["url"]) for k in so_portal],
        ("titulo_portal", "url"),
    )
    write_csv(
        out / "banco_so.csv",
        [(banco[k][0], banco[k][1]) for k in so_banco],
        ("titulo_banco", "slug_servico"),
    )

    (out / "resumo.md").write_text(
        f"# Portal MS x banco — `{args.categoria}`\n\n"
        f"- Portal (admin.ms.gov.br/api, ativos): **{len(portal)}**\n"
        f"- Banco (admin_prd, ativos, tema.slug = `{args.categoria}`): **{len(banco)}**\n"
        f"- Interseção: **{intersec}**\n"
        f"- Só no portal: **{len(so_portal)}**\n"
        f"- Só no banco: **{len(so_banco)}**\n\n"
        f"Snapshot bruto da API: `{raw}`\n",
        encoding="utf-8",
    )

    print(f"[portal:{args.categoria}]   {len(portal)}")
    print(f"[banco:{args.categoria}]    {len(banco)}")
    print(f"[intersecao]                {intersec}")
    print(f"[so_portal]                 {len(so_portal)}")
    print(f"[so_banco]                  {len(so_banco)}")
    print(f"[ok] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
