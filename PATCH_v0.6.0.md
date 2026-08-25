# PATCH v0.6.0 — Decision Intelligence

**Tipo: PATCH INCREMENTAL**

Aplicar diretamente em:

`C:\inti_intelligence\INTI_Intelligence`

Não cria nova pasta e não altera `data/snapshots`.

## Novos arquivos
- `src/inti_intelligence/decision_intelligence.py`
- `scripts/build_decision_intelligence.py`
- `tests/test_decision_intelligence.py`
- `PATCH_v0.6.0.md`

## Arquivos substituídos
- `dashboard/app.py`
- `CHANGELOG.md`
- `VERSION`

## Novos outputs
- `data/output/category_decision_map.csv`
- `data/output/executive_actions.csv`
- `data/output/decision_kpis.json`

## Execução
```powershell
$env:PYTHONPATH = "$PWD\src"
python .\scripts\build_decision_intelligence.py
python -m pytest -q
python -m streamlit run .\dashboard\app.py
```
