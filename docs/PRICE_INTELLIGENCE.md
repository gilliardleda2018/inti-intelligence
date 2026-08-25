# INTI Sprint 3.1 — Price Intelligence

Patch incremental para a raiz interna do Sprint 3.

## O que adiciona
- enriquecimento de preço das variantes a partir das URLs do Snapshot 01;
- checkpoint e `--resume` para evitar perder progresso;
- retries via nova execução (linhas processadas são preservadas);
- cobertura/confiança de preço;
- KPIs de preço e markdown;
- resumo por categoria;
- radar dos maiores markdowns;
- página **Price Intelligence** no cockpit.

## Instalação
Extraia este ZIP diretamente na raiz interna do Sprint 3, permitindo sobrescrever `dashboard/app.py` e `src/inti_intelligence/price_parser.py`.

## Execução
Teste curto opcional:

```powershell
python .\scripts\enrich_prices.py --limit 20
```

Para o catálogo completo:

```powershell
python .\scripts\enrich_prices.py
```

O padrão usa pausa de 1 segundo entre páginas e checkpoint em `data/output/price_enrichment_checkpoint.csv`.

Depois:

```powershell
python -m streamlit run .\dashboard\app.py
```

## Outputs
- `data/output/catalog_enriched_latest.csv`
- `data/output/price_enrichment_checkpoint.csv`
- `data/output/price_enrichment_failures.csv`
- `data/output/price_kpis.json`
- `data/output/price_by_category.csv`
- `data/output/top_markdowns.csv`
