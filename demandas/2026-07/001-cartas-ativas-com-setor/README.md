# 001 — Cartas ativas com setor

- **Solicitante**: Fabio Ramos (SETDIG)
- **Abertura**: 2026-07-15
- **Entrega**: 2026-07-15
- **Objetivo**: Exportar do banco `admin_prd` todas as cartas ativas com as colunas
  `siglaorgao | setor | titulo_servico | categoria | url` em XLSX único.

## Reproduzir

```bash
python scripts/extract_cartas_ativas_com_setor.py \
  --out demandas/2026-07/001-cartas-ativas-com-setor/output/cartas-ativas-com-setor.xlsx
```

## Notas

- `siglaorgao` vem de `gerenciamento_orgaos.sigla` via `servicos.setor_id → setor.orgao_id`.
- `setor` vem de `gerenciamento_setor.nome` (mesmo caminho).
- `categoria` = `gerenciamento_temas.slug`.
- `url` = `https://www.ms.gov.br/<categoria>/<slug_servico>`.
- Linhas sem setor/órgão/tema saem vazias no respectivo campo (script imprime contagens).
