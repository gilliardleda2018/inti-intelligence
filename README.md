# INTI Intelligence

**Version 0.3.1 — Consolidated Full Build**

Projeto único para Catalog Intelligence, Price Intelligence, Temporal Intelligence e evolução futura para Demand & Inventory Intelligence.

## Regra de estrutura

A partir desta versão existe **uma única raiz oficial**:

```text
C:\inti_intelligence\INTI_Intelligence
```

Novas entregas deverão ser identificadas explicitamente como:

- **FULL BUILD** — pacote completo, mantendo toda a estrutura.
- **PATCH INCREMENTAL** — somente arquivos alterados, com instruções exatas de destino.

Nenhuma nova sprint deve criar uma pasta paralela do projeto.

## Estrutura

```text
INTI_Intelligence/
├── app/                    # API FastAPI / MVP analítico
├── collectors/             # Real Catalog Collector
├── dashboard/              # Premium Cockpit
├── data/
│   ├── output/             # saídas analíticas
│   ├── snapshots/          # snapshots temporais
│   └── synthetic/          # dados sintéticos de apoio
├── scripts/
│   ├── build_sprint3.py
│   ├── compare_latest_snapshots.py
│   ├── price_probe.py
│   ├── enrich_prices.py
│   ├── catalog_summary.py
│   └── generate_synthetic_data.py
├── src/inti_intelligence/  # normalizer, temporal, price parser/intelligence
├── tests/
├── requirements.txt
├── CHANGELOG.md
├── VERSION
└── README.md
```

## Estado preservado

- Snapshot 01: catálogo público real da INTI.
- 587 variantes.
- 401 produtos-base.
- 2.635 posições variante × tamanho.
- 14 categorias.
- 29 cores.
- Price Probe: 10/10 páginas com preço extraído via JSON-LD e confiança HIGH.
- Disponibilidade do Snapshot 01 permanece marcada como não confiável.
- Não criar Snapshot 02 antes de concluir o Price Enrichment.

## Instalação no Windows

```powershell
cd C:\inti_intelligence\INTI_Intelligence
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\requirements.txt
```

## Próximo passo atual: Price Intelligence completo

```powershell
python .\scripts\enrich_prices.py
```

O processo é retomável por checkpoint.

Depois:

```powershell
python -m streamlit run .\dashboard\app.py
```

## Coletor público

Teste controlado:

```powershell
python -m collectors.inti_catalog --max-products 5
```

Coleta completa futura somente quando planejarmos um novo snapshot:

```powershell
python -m collectors.inti_catalog
```

## Testes

```powershell
python -m pytest -q
```

## Nota metodológica

Sinais do catálogo público não devem ser descritos como vendas reais. Preço e disponibilidade só alimentam indicadores quando passam pelos respectivos quality gates.
