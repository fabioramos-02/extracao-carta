# 002 — Histórico de atualizações das cartas de serviço

- **Solicitante**: Ariane Sodré (Comunicação, SETDIG/SGD)
- **Abertura**: 2026-11-09
- **Entrega**: 2026-11-09
- **Objetivo**: comprovar que as cartas de serviço ativas no Portal são atualizadas: versão atual,
  número de edições e revisões, e data da última alteração de cada carta.

## Reproduzir

```bash
python scripts/extract_atualizacoes_cartas.py \
  --out demandas/2026-11/002-atualizacoes-cartas/output/atualizacoes-cartas.xlsx
```

## Notas

- Fonte: `gerenciamento_historicoservico` (cada criação, edição, revisão e mudança de etapa gera
  um registro com `versao`) e `gerenciamento_revisaoservico` (data da revisão periódica).
- Só registros `aprovado = true`: pendentes e recusados não chegaram ao Portal.
- Só cartas `ativo = true`, o mesmo filtro da API do Portal.
- Sem nome de usuário na planilha.
- Extração de 09/11/2026: 1.236 cartas ativas, 24.666 alterações aprovadas desde 04/2023,
  1.003 cartas alteradas em 2026, versão máxima 83.
- Dado do sistema atual de cartas; as cartas estão migrando para o novo CMS.
