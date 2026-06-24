# 004 — Cartas ativas (export completo)

- **Solicitante**: Daniele (SGD)
- **Abertura**: 2026-06-24
- **Entrega**: 2026-06-24
- **Objetivo**: Exportar do banco `admin_prd` todas as cartas ativas com as colunas
  `siglaorgao | titulo_servico | categoria | url` em XLSX único.

## Reproduzir

```bash
python scripts/extract_cartas_ativas.py \
  --out demandas/2026-06/004-cartas-ativas-completo/output/cartas-ativas.xlsx
```

## Notas

- `siglaorgao` vem de `gerenciamento_orgaos.sigla` via `servicos.setor_id → setor.orgao_id`.
- `categoria` = `gerenciamento_temas.slug`.
- `url` = `https://www.ms.gov.br/<categoria>/<slug_servico>` (mesmo padrão do portal).
- Linhas sem setor/órgão ou sem tema saem com string vazia no respectivo campo
  (script imprime contagem `sem sigla_orgao` / `sem categoria`).
