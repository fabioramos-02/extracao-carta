# extracao-carta — convenções do projeto

Repo de uso recorrente para **extrair dados da Carta de Serviços** (banco `admin_prd`) e
**gerar relatórios/planilhas enriquecidas** sob demanda de áreas internas (SEFAZ, SAD, etc.).

## Princípios

- **SRP**: um arquivo, uma responsabilidade. Sem god-modules.
- **≤ 250 linhas por arquivo**. Se passar, fatiar.
- **Sem segredo no repo**: `.env` é gitignored. Usar `.env.example` como template.
- **Demandas ficam isoladas em pastas datadas** (ver layout abaixo). O código `src/` é genérico
  e reutilizável; cada demanda só consome os módulos via `scripts/`.
- **Match de nomes**: sempre via `extracao_carta.normalize.normalize()`
  (NFKD + remove acentos/pontuação + colapsa espaços + lower). Nunca match literal.
- **Conexão DB**: sempre via `extracao_carta.db.connect()`. Não duplicar `psycopg2.connect`.

## Layout

```
src/extracao_carta/   # biblioteca interna reutilizável
    db.py             # connect() + load_env()
    normalize.py      # normalize(s)
    queries.py        # SQLs nomeados + funções que retornam dicts
    xlsx.py           # leitura/escrita openpyxl preservando formatação
scripts/              # entrypoints CLI finos (parse args, chama src/)
demandas/<AAAA-MM>/<NNN-slug>/
    README.md         # contexto: quem pediu, o que entregar, prazo
    input/            # planilhas/CSVs originais recebidos (não editar)
    output/           # artefatos gerados (versionar se útil)
```

## Convenção de pastas de demanda (estilo GCS)

- **Bucket virtual**: `demandas/`
- **Prefixo temporal**: `AAAA-MM` (mês da abertura).
- **Slug**: `NNN-kebab-case`, onde `NNN` é sequencial dentro do mês (`001`, `002`, ...).
- Exemplo: `demandas/2026-06/001-categorias-sefaz/`.
- Cada demanda **deve** ter `README.md` próprio com: solicitante, descrição, data de abertura,
  data de entrega, comando exato para reproduzir.

## Fluxo padrão de nova demanda

1. Criar `demandas/AAAA-MM/NNN-slug/{input,output}` + `README.md` (template abaixo).
2. Colocar arquivos recebidos em `input/`. Nunca editá-los.
3. Se a lógica não existe em `src/`, adicionar módulo respeitando SRP/250 linhas.
4. Criar/usar script em `scripts/` apontando para `input/` → `output/`.
5. Atualizar `README.md` da demanda com o comando reproduzível.

## Template — `demandas/.../README.md`

```markdown
# NNN — <título curto>

- **Solicitante**: <nome / área>
- **Abertura**: AAAA-MM-DD
- **Entrega**: AAAA-MM-DD
- **Objetivo**: <1 parágrafo>

## Reproduzir

\`\`\`bash
python scripts/<script>.py --in demandas/.../input/<arquivo> --out demandas/.../output/<arquivo>
\`\`\`

## Notas

- <colisões, decisões, anomalias>
```

## Banco

- Servidor: PostgreSQL corporativo (`admin_prd`).
- Tabelas frequentes: `gerenciamento_servicos`, `gerenciamento_temas`, `gerenciamento_setor`, `gerenciamento_orgaos`.
- Categoria do serviço = `gerenciamento_temas.slug` via `s.tema_id`.

## Não fazer

- Não commitar `.env`, `~$*.xlsx`, dumps de banco.
- Não criar scripts ad-hoc na raiz: sempre `scripts/<nome>.py`.
- Não duplicar `normalize` ou `connect`: importe de `src/`.
- Não embarcar credenciais em código.
