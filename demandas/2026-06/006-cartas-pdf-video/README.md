# 006 — Cartas com PDF e Vídeo

- **Solicitante**: Equipe de Carta de Serviços / SETDIG
- **Abertura**: 2026-06-30
- **Entrega**: —
- **Objetivo**: Identificar todas as cartas de serviço ativas que possuem URL de PDF
  ou link de vídeo (YouTube/Vimeo) em qualquer seção de conteúdo, para auditoria de
  conformidade (ex.: detecção de logo política em PDFs).

## Reproduzir

```bash
python scripts/extract_cartas_pdf_video.py \
  --out demandas/2026-06/006-cartas-pdf-video/output/cartas-pdf-video.xlsx
```

## Colunas do XLSX

| Coluna         | Descrição                                   |
|----------------|---------------------------------------------|
| sigla_orgao    | Sigla do órgão responsável                  |
| titulo_servico | Título da carta de serviço                  |
| categoria      | Slug do tema (categoria)                    |
| url_carta      | Link da carta no portal ms.gov.br           |
| secao          | Coluna de origem (ex: `descricao`)          |
| tipo           | `pdf` ou `video`                            |
| url_midia      | URL extraída do HTML da seção               |
| logo_politica  | Preenchimento manual: `presente` / `ausente`|

## Seções monitoradas

- `descricao` → O que é este serviço?
- `requisitos` → Exigências para realizar o serviço
- `publico` → Quem pode utilizar este serviço?
- `publico_especifico` → Quem pode utilizar (específico)
- `tempo_total` → Prazos
- `informacoes_extra` → Outras informações

## Notas

- Conteúdo das seções é HTML — URLs extraídas via `<a href>` e `<iframe src>`.
- Colunas `custo` e `etapas` não confirmadas no schema; adicionar se existirem.
- `logo_politica` fica vazia para preenchimento manual carta a carta.
