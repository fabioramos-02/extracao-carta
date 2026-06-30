"""CLI: extrai cartas ativas com URL de PDF ou vídeo e gera XLSX para auditoria.

Colunas: sigla_orgao | titulo_servico | categoria | url_carta |
         secao | tipo | url_midia | logo_politica

Uso:
    python scripts/extract_cartas_pdf_video.py \\
        --out demandas/2026-06/006-cartas-pdf-video/output/cartas-pdf-video.xlsx
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from extracao_carta.db import connect, load_env  # noqa: E402
from extracao_carta.queries import (  # noqa: E402
    PORTAL_URL_BASE,
    SECOES,
    cartas_secoes_brutas,
)
from extracao_carta.url_extract import extract_urls  # noqa: E402

HEADERS = (
    "sigla_orgao",
    "titulo_servico",
    "categoria",
    "url_carta",
    "secao",
    "tipo",
    "url_midia",
    "logo_politica",
)


_DEFAULT_OUT = (
    Path(__file__).resolve().parents[1]
    / "demandas/2026-06/006-cartas-pdf-video/output/cartas-pdf-video.xlsx"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Exporta cartas com PDF/vídeo para XLSX."
    )
    p.add_argument("--env", default=".env")
    p.add_argument("--out", dest="out_path", type=Path, default=_DEFAULT_OUT)
    return p.parse_args()


def _build_rows(raw: list[tuple]) -> list[tuple]:
    rows: list[tuple] = []
    for record in raw:
        sigla, titulo, categoria, slug, *secao_vals = record
        url_carta = (
            f"{PORTAL_URL_BASE}/{categoria}/{slug}"
            if categoria and slug
            else ""
        )
        for secao, html in zip(SECOES, secao_vals):
            for item in extract_urls(html):
                rows.append((
                    sigla,
                    titulo,
                    categoria,
                    url_carta,
                    secao,
                    item["tipo"],
                    item["url"],
                    "",
                ))
    return rows


def _write_xlsx(path: Path, rows: list[tuple]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "pdf_video"
    ws.append(HEADERS)
    for r in rows:
        ws.append(r)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def main() -> int:
    args = parse_args()
    load_env(args.env)
    with connect() as conn:
        raw = cartas_secoes_brutas(conn)
    rows = _build_rows(raw)
    _write_xlsx(args.out_path, rows)
    pdfs = sum(1 for r in rows if r[5] == "pdf")
    videos = sum(1 for r in rows if r[5] == "video")
    cartas_unicas = len({r[1] for r in rows})
    print(f"[db] cartas ativas varridas: {len(raw)}")
    print(f"[ok] cartas com mídia: {cartas_unicas} | PDFs: {pdfs} | vídeos: {videos}")
    print(f"[ok] gravado: {args.out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
