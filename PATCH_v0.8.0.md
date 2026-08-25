# PATCH v0.8.0 — Product Similarity & Portfolio ML

**PATCH INCREMENTAL** para `C:\inti_intelligence\INTI_Intelligence`.
Não cria projeto paralelo e não altera snapshots.

## Instalação adicional
`python -m pip install -r requirements_v0.8_add.txt`

## Execução
`$env:PYTHONPATH = "$PWD\src"`
`python .\scripts\build_portfolio_ml.py`
`python -m pytest -q`
`python -m streamlit run .\dashboard\app.py`

## Outputs
- product_ml_space.csv
- product_neighbors.csv
- near_duplicate_radar.csv
- portfolio_clusters.csv
- white_space_candidates.csv
- portfolio_ml_kpis.json
