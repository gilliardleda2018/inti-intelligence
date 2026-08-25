# PATCH INCREMENTAL — INTI Intelligence v0.4.0

**Base obrigatória:** v0.3.1 FULL BUILD.

Este pacote **não cria uma nova pasta de projeto**. Extraia seu conteúdo dentro de:

`C:\inti_intelligence\INTI_Intelligence`

permitindo substituir os arquivos existentes.

## Arquivos atualizados
- `dashboard/app.py`
- `src/inti_intelligence/data_layer.py` (novo)
- `src/inti_intelligence/commercial_intelligence.py` (novo)
- `scripts/build_commercial_intelligence.py` (novo)
- `tests/test_data_layer.py` (novo)
- `tests/test_commercial_intelligence.py` (novo)
- `CHANGELOG.md`
- `VERSION`

## Depois de aplicar

```powershell
cd C:\inti_intelligence\INTI_Intelligence
.\.venv\Scripts\Activate.ps1
python .\scripts\build_commercial_intelligence.py
python -m pytest -q
python -m streamlit run .\dashboard\app.py
```

O patch usa o `catalog_enriched_latest.csv` já produzido pelo Price Enrichment. Não refaça o catálogo e não crie Snapshot 02 ainda.
