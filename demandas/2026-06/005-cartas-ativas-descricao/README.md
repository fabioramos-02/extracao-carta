# 005 — Cartas ativas com descrição (o que é o serviço)

- **Solicitante**: interno SETDIG
- **Abertura**: 2026-06-26
- **Entrega**: 2026-06-26
- **Objetivo**: gerar XLSX de todas as cartas ativas do banco `admin_prd` com colunas
  `siglaorgao`, `titulo_servico`, `categoria`, `url`, `o_que_e_servico`.

## Reproduzir

```bash
python scripts/extract_cartas_ativas_descricao.py \
    --out demandas/2026-06/005-cartas-ativas-descricao/output/cartas-ativas.xlsx
```

## Notas

- `o_que_e_servico` = `gerenciamento_servicos.descricao`.
- `url` = `https://www.ms.gov.br/<categoria>/<slug_servico>` quando categoria e slug existem.
- Filtro: `s.ativo = true AND s.titulo IS NOT NULL`.
