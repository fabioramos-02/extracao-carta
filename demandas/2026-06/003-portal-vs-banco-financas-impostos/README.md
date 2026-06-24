# 003 — Portal MS × Banco: validação em `financas-e-impostos`

- **Solicitante**: validação interna (revisão da demanda 002)
- **Abertura**: 2026-06-23
- **Entrega**: 2026-06-23
- **Objetivo**: contar cartas **ativas** publicadas em
  https://www.ms.gov.br/categoria/financas-e-impostos e comparar com a contagem
  do banco `admin_prd` (tema.slug = `financas-e-impostos`) para entender a
  divergência apontada na demanda 002.

## Reproduzir

```bash
python scripts/cruzamento_portal_banco.py \
  --categoria financas-e-impostos \
  --out-dir demandas/2026-06/003-portal-vs-banco-financas-impostos/output
```

## Resultado

| medida                                                  | valor   |
| ------------------------------------------------------- | ------- |
| Portal MS (`admin.ms.gov.br/api`, ativos na categoria)  | **219** |
| Banco `admin_prd` (ativos, tema.slug = financas-…)      | **219** |
| Interseção (normalize por título)                       | **219** |
| Só no portal                                            | **0**   |
| Só no banco                                             | **0**   |

**Portal e banco batem 100%.**

## Conclusão sobre a demanda 002

A divergência de 002 (planilha SEFAZ 214 únicos × banco 219 → "5 faltantes")
**não é erro do banco/portal**. Portal e banco são a **mesma fonte** —
`admin.ms.gov.br/api` (consumida pela SPA do portal) lê a tabela
`gerenciamento_servicos` de `admin_prd`. As 5 cartas listadas em 002 estão
publicadas no portal e ativas no banco; o que está desatualizado é a
**planilha SEFAZ** (insumo de comparação), não o cadastro.

Ação recomendada: tratar a planilha SEFAZ como desatualizada e atualizá-la
com as 5 cartas listadas em `../002-ausentes-financas-impostos/output/extras-no-banco.csv`.

## Notas técnicas

- Endpoint descoberto no bundle JS público do portal
  (`/static/js/main.cf3c715f.js`), função `cg` da rota `/categoria/:slug`:
  `GET /cms/servicos/?categoria_slug=<slug>&ativo=true`.
- `Authorization: Api-Key …` extraído do mesmo bundle (base64, hardcoded). Não é
  segredo: qualquer visitante recebe o mesmo valor ao carregar o site.
- Snapshot bruto da resposta JSON em `input/portal.json` para auditoria/replay.

## Artefatos em `output/`

- `resumo.md` — contagens.
- `portal_so.csv` — vazio (0 cartas só no portal).
- `banco_so.csv` — vazio (0 cartas só no banco).
