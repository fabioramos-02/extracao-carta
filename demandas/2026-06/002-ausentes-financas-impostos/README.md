# 002 — Cartas faltantes na planilha SEFAZ (categoria `financas-e-impostos`)

- **Solicitante**: colega de equipe (relato verbal)
- **Abertura**: 2026-06-23
- **Objetivo**: extrair do banco `admin_prd` as cartas ativas com
  `tema.slug = financas-e-impostos`, comparar com a planilha SEFAZ e listar as
  cartas do banco que **faltam** na planilha.

## Reproduzir

```bash
python scripts/cruzamento_ausentes.py \
  --in demandas/2026-06/002-ausentes-financas-impostos/input/Cópia\ de\ Categorias\ SEFAZ.xlsx \
  --categoria financas-e-impostos \
  --mode mapped \
  --out-dir demandas/2026-06/002-ausentes-financas-impostos/output
```

## Resultado

| medida                                                    | valor |
| --------------------------------------------------------- | ----- |
| Banco — cartas ativas em `financas-e-impostos`            | 219   |
| Planilha — únicos cujo título o banco classifica em `financas-e-impostos` | 214 |
| **Faltantes na planilha (banco − planilha)**              | **5** |

### Lista das 5 faltantes — `output/extras-no-banco.csv`

| título no banco | slug |
| --- | --- |
| Declaração para fins de proporcionalização ou isenção do desconto do INSS acima do teto | declaracao-para-fins-de-proporcionalizacao-ou-isencao-do-desconto-do-inss-acima-do-teto109 |
| Emitir DAEMS – pagar emolumentos e taxas à PGE | emitir-daems-pagar-emolumentos-e-taxas-a-pge132 |
| ICMS Diferencial de Alíquotas - dispensa da cobrança na aquisição de maquinário por industrial ou produtor rural | icms-diferencial-de-aliquotas-dispensa-da-cobranca-na-aquisicao-de-maquinario-por-industrial-ou-produtor-rural84 |
| Parcelar débitos de taxa de fiscalização e de multas da AGEMS | pedir-parcelamento-de-debitos-de-taxa-de-fiscalizacao-e-de-multas-de-competencia-da-agems144 |
| Verificar recolhimento do ITCD em processos de inventário e similares | verificacao-do-recolhimento-do-itcd70 |

## Esclarecimento sobre o "19" do relato inicial

Relato: "planilha 238, banco 219, diferença 19".

| medida                                                            | valor |
| ----------------------------------------------------------------- | ----- |
| Linhas (com duplicatas em subcategorias) na planilha cuja categoria-banco é `financas-e-impostos` | 238   |
| Únicos correspondentes                                            | 214   |

Os **238** contam linhas com repetição (a mesma carta aparece em mais de uma
subcategoria da planilha). Como cartas únicas, são **214**. A diferença real
contra o banco (219) é portanto **5**, não 19.

## Artefatos em `output/`

- `extras-no-banco.csv` — **a lista pedida**: 5 cartas no banco financas que faltam na planilha.
- `ausentes-no-banco.csv` — 0 (todas as 214 cartas mapeadas da planilha existem no banco financas).
- `resumo.md` — contagens consolidadas.

## Recomendação

Verificar com a colega se as 5 cartas faltantes devem ser incluídas na planilha
SEFAZ (cadastro novo) ou se a categoria no banco para alguma delas está errada.
