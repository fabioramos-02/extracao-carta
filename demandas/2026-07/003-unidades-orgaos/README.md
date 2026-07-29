# 003 — Unidades de todos os órgãos + modelagem lógica de unidades

- **Solicitante**: interno / SETDIG
- **Abertura**: 2026-07-29
- **Entrega**: 2026-07-29
- **Objetivo**: exportar em XLSX **todas as unidades** cadastradas em
  `gerenciamento_unidades`, com identificação do órgão vinculado
  (sigla + nome), endereço, cidade/estado e situação. A planilha usa
  `auto_filter` no header — filtragem por `sigla_orgao`, `nome_orgao`,
  `cidade`, `estado` ou `ativo` direto no Excel. Entrega junto a
  documentação Markdown com Diagrama Entidade-Relacionamento (ER) da
  tabela `gerenciamento_unidades` e seus relacionamentos com
  `gerenciamento_orgaos` e `gerenciamento_cidades`.

## Reproduzir

```bash
python scripts/extract_unidades.py \
  --out demandas/2026-07/003-unidades-orgaos/output/unidades.xlsx
```

## Notas

- Escopo inicial era só DETRAN (a demanda referia "DER", sigla que não
  existe no banco). Refatorado para "todos os órgãos" a pedido do
  solicitante — o filtro no XLSX cobre o caso DETRAN e qualquer outro.
- `gerenciamento_unidades` **não declara FK** para `orgaos` nem
  `cidades`. O join é feito por convenção (`orgao_id` → `orgaos.id`,
  `cidade_id` → `cidades.slug`). Ver
  [docs/modelagem-unidades.md](docs/modelagem-unidades.md).
- `cidade_id` é `varchar` (guarda o slug da cidade, não um inteiro).
- Coluna `source` na tabela **não indica origem do registro** apesar
  do nome: guarda a URL do `<iframe>` embed do Google Maps da unidade.
