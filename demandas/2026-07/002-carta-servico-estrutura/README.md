# 002 — Estrutura da carta de serviço (MER/DER) + cartas ativas

- **Solicitante**: Analista de Negócio e Líder Técnico (XVia / migração EDS)
- **Abertura**: 2026-07-28
- **Entrega**: 2026-07-28
- **Objetivo**: mostrar quantas cartas de serviço existem e como estão estruturadas no
  banco. Duas peças: um documento com MER/DER e a planilha das cartas ativas com as
  seções da carta em texto plano.

## Reproduzir

```bash
python scripts/extract_cartas_ativas_completo.py --out ../mapeamento-banco-eds/docs/cartas-servico-ativas.xlsx
```

Saída gravada fora deste repo, junto do documento que a referencia:
`SETDIG/2026/Projetos/mapeamento-banco-eds/docs/`.

## Resultado (28/07/2026)

- 1.227 cartas ativas (de 1.522 serviços cadastrados)
- 40 órgãos · 314 setores · 21 categorias
- 15.724 vínculos serviço ↔ unidade
- 1.202 cartas (98%) com `id_servico_govbr`

## Notas

- Query nova `CARTAS_ATIVAS_ESTRUTURA` (`src/extracao_carta/queries.py`): une a
  identificação de `CARTAS_ATIVAS_COM_SETOR` com as seções de `CARTAS_SECOES_BRUTAS`.
  Não estendemos `CARTAS_SECOES_BRUTAS` porque `extract_cartas_pdf_video.py` consome
  aquela tupla por posição.
- `descricao`, `requisitos`, `custo`, `publico` e `informacoes_extra` são HTML cru no
  banco. Convertidos para texto plano por `src/extracao_carta/html_text.py` (stdlib
  `HTMLParser`, sem dependência nova). Self-check: `python src/extracao_carta/html_text.py`.
- `tempo_total` = `0` em 142 cartas. É "não informado", não "imediato" — a coluna é
  `smallint NOT NULL`, então não existe nulo para distinguir.
- Contagem subiu de 1.225 (demanda 2026-07/001, extraída em 15/07) para 1.227.
