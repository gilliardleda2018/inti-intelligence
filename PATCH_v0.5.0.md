# PATCH v0.5.0 — Assortment & Merchandising Intelligence

**Tipo de entrega: PATCH INCREMENTAL.**

Aplicar sobre a raiz existente:

`C:\inti_intelligence\INTI_Intelligence`

Não cria projeto paralelo e não altera/apaga `data/snapshots`.

## Arquivos novos
- `src/inti_intelligence/assortment_intelligence.py`
- `scripts/build_merchandising_intelligence.py`
- `tests/test_assortment_intelligence.py`
- `PATCH_v0.5.0.md`

## Arquivos substituídos
- `dashboard/app.py`
- `CHANGELOG.md`
- `VERSION`

## Novos outputs
- `data/output/assortment_kpis.json`
- `data/output/assortment_by_category.csv`
- `data/output/color_architecture.csv`
- `data/output/variant_density.csv`
- `data/output/size_coverage.csv`
- `data/output/merchandising_opportunities.csv`

## Execução
```powershell
python .\scripts\build_merchandising_intelligence.py
python -m pytest -q
python -m streamlit run .\dashboard\app.py
```
