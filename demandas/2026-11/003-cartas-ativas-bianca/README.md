# 003 — Cartas ativas com todos os campos (Bianca)

- **Solicitante**: Bianca Martins Coelho (SETDIG/SGD)
- **Abertura**: 2026-11-12
- **Entrega**: 2026-11-12
- **Objetivo**: entregar todas as cartas de serviço ativas do sistema atual (EDS, banco `admin_prd`)
  com os campos da carta, uma linha por carta.

## Reproduzir

```bash
python scripts/extract_cartas_ativas_completo.py --out demandas/2026-11/003-cartas-ativas-bianca/output/cartas-ativas-completo.xlsx
```

## Resultado (12/11/2026)

- 1.236 cartas ativas, 40 órgãos, 21 categorias.
- 14 colunas: orgao_sigla, setor, titulo_servico, categoria, url, o_que_e, requisitos, custo,
  publico, publico_especifico, tempo_total, informacoes_extra, agendavel, digital.

## Notas

- Mesmo script da demanda `2026-06/004-cartas-ativas-completo`; só cartas `ativo = true`
  (filtro do Portal). Seções em HTML convertidas para texto.
- Etapas ficam fora (ver `2026-11/001-cartas-etapas`), por decisão do Fabio.
