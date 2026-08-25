from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from inti_intelligence.data_layer import load_catalog_bundle
from inti_intelligence.commercial_intelligence import commercial_kpis, category_commercial_summary, markdown_pressure_by_category, add_price_tiers

bundle = load_catalog_bundle(ROOT)
if not bundle.enriched:
    raise SystemExit('Price-enriched catalog not found. Run: python .\\scripts\\enrich_prices.py')
out = ROOT / 'data' / 'output'; out.mkdir(parents=True, exist_ok=True)
cat = bundle.catalog
kpis = commercial_kpis(cat)
(out / 'commercial_kpis.json').write_text(json.dumps(kpis, ensure_ascii=False, indent=2), encoding='utf-8')
category_commercial_summary(cat).to_csv(out / 'commercial_by_category.csv', index=False, encoding='utf-8-sig')
markdown_pressure_by_category(cat).to_csv(out / 'markdown_pressure_by_category.csv', index=False, encoding='utf-8-sig')
add_price_tiers(cat).to_csv(out / 'catalog_commercial_latest.csv', index=False, encoding='utf-8-sig')
print('INTI Commercial Intelligence v0.4')
print('--------------------------------')
print(f'source: {bundle.source_name}')
for k, v in kpis.items(): print(f'{k}: {v}')
print(f'Output: {out}')
