# PATCH INCREMENTAL v0.4.1 — Commercial Temporal Intelligence

**Destino:** `C:\inti_intelligence\INTI_Intelligence`

Este pacote mantém a estrutura única do projeto. Não cria diretório paralelo.

## Arquivos novos
- `src/inti_intelligence/commercial_temporal.py`
- `scripts/compare_commercial_snapshots.py`
- `tests/test_commercial_temporal.py`
- `PATCH_v0.4.1.md`

## Arquivos substituídos
- `dashboard/app.py`
- `src/inti_intelligence/temporal.py`
- `CHANGELOG.md`
- `VERSION`

## Execução

```powershell
cd C:\inti_intelligence\INTI_Intelligence
.\.venv\Scripts\Activate.ps1
python .\scripts\compare_commercial_snapshots.py
python -m pytest -q
python -m streamlit run .\dashboard\app.py
```

## Saídas
- `data/output/commercial_temporal_events.csv`
- `data/output/commercial_temporal_kpis.json`
- `data/output/commercial_temporal_comparison.csv`

## Metodologia
Commercial Temporal Intelligence compara apenas sinais públicos observáveis de preço e markdown. Não infere vendas, demanda, estoque interno ou preço realizado.
