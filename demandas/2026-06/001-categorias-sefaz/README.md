# 001 — Categorias SEFAZ

- **Solicitante**: SEFAZ-MS (via colega de equipe)
- **Abertura**: 2026-06-23
- **Entrega**: 2026-06-23
- **Objetivo**: enriquecer a planilha `Cópia de Categorias SEFAZ.xlsx` (colunas
  `Subcategoria` + `Carta de serviço`) com uma terceira coluna `categoria`
  contendo o `tema.slug` do banco `admin_prd` para cada carta listada.

## Reproduzir

```bash
python scripts/enrich_categorias.py \
  --in  demandas/2026-06/001-categorias-sefaz/input/Cópia\ de\ Categorias\ SEFAZ.xlsx \
  --out demandas/2026-06/001-categorias-sefaz/output/categorias-sefaz-enriched.xlsx
```

## Resultado

- Total de linhas com nome de carta: **299**
- Casadas com `gerenciamento_servicos.titulo`: **299**
- Sem match: **0**

## Notas

3 colisões observadas (mesmo título normalizado aparece em temas distintos no banco) —
script usa o primeiro slug e loga warning em stderr:

- `fazer pedido de acesso a informacao` → `administracao-publica` / `comunicacao-e-transparencia` / `direitos-e-cidadania`
- `registrar denuncia` → `administracao-publica` / `comunicacao-e-transparencia` / `direitos-e-cidadania` / `meio-ambiente` / `seguranca`
- `registrar reclamacao solicitacao sugestao e elogio` → `administracao-publica` / `comunicacao-e-transparencia` / `direitos-e-cidadania`

Nenhuma das três aparece na planilha SEFAZ, então não impacta o resultado entregue.
