# extracao-carta

Toolkit para **extrair dados da Carta de Serviços do Governo de Mato Grosso do Sul** (banco
`admin_prd`) e gerar planilhas/relatórios enriquecidos sob demanda das áreas da
[SETDIG](https://www.setdig.ms.gov.br/) e parceiras.

> Mantido por [Secretaria-Executiva de Transformação Digital — SETDIG/SEGOV/MS](https://www.setdig.ms.gov.br/).

## Visão

Cada demanda recebida (de SEFAZ, SAD, áreas internas etc.) é isolada em uma pasta datada
dentro de `demandas/`, contendo o material original (`input/`), o resultado (`output/`) e
um `README.md` próprio com contexto e comando reproduzível. O código de extração é
genérico, reutilizável e fica em `src/extracao_carta/`.

## Layout

```
.
├── src/extracao_carta/       # biblioteca: db, normalize, queries, xlsx
├── scripts/                  # entrypoints CLI
├── demandas/<AAAA-MM>/<NNN-slug>/
│   ├── input/                # arquivos recebidos (imutáveis)
│   ├── output/               # artefatos gerados
│   └── README.md             # contexto da demanda
├── .env.example
├── requirements.txt
└── CLAUDE.md                 # convenções para colaboradores e IA
```

## Setup

```bash
git clone <repo>
cd extracao-carta
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # preencher credenciais do banco
```

Variáveis obrigatórias no `.env`:

| chave         | descrição                       |
| ------------- | ------------------------------- |
| `DB_HOST`     | host PostgreSQL                 |
| `DB_PORT`     | porta (geralmente 5432)         |
| `DB_USER`     | usuário                         |
| `DB_PASSWORD` | senha                           |
| `DB_NAME`     | nome do banco (ex: `admin_prd`) |

## Scripts disponíveis

### `enrich_categorias.py` — adiciona coluna `categoria` (tema.slug) a uma planilha

```bash
python scripts/enrich_categorias.py \
  --in  demandas/2026-06/001-categorias-sefaz/input/Cópia\ de\ Categorias\ SEFAZ.xlsx \
  --out demandas/2026-06/001-categorias-sefaz/output/categorias-sefaz-enriched.xlsx
```

Match contra `gerenciamento_servicos.titulo` (normalizado: lower + sem acento + sem
pontuação + espaços colapsados). Categoria escrita = `gerenciamento_temas.slug`.

Flags opcionais:

| flag           | default | descrição                            |
| -------------- | ------- | ------------------------------------ |
| `--env`        | `.env`  | caminho do arquivo de variáveis      |
| `--lookup-col` | `2`     | coluna do nome do serviço (1-based)  |
| `--write-col`  | `3`     | coluna onde gravar a categoria       |

## Nova demanda — passo a passo

1. Crie a pasta:
   ```bash
   mkdir -p demandas/2026-07/002-minha-demanda/{input,output}
   ```
2. Copie material recebido para `input/`.
3. Crie `demandas/2026-07/002-minha-demanda/README.md` (template em [CLAUDE.md](CLAUDE.md)).
4. Reutilize ou adicione script em `scripts/` (módulos em `src/extracao_carta/`).
5. Rode o script apontando `--in`/`--out` para a pasta da demanda.

## Padrões de código

- SRP: 1 arquivo = 1 responsabilidade.
- Máx **250 linhas** por arquivo.
- Sempre importe `connect` de `extracao_carta.db` e `normalize` de `extracao_carta.normalize`.
- Conventional Commits nos commits.
- Veja [CLAUDE.md](CLAUDE.md) para convenções completas.

## Licença

A definir.
