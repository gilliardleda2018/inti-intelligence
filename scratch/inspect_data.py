import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from inti_intelligence.commercial_intelligence import commercial_kpis, category_commercial_summary
from inti_intelligence.assortment_intelligence import assortment_kpis, category_architecture
from inti_intelligence.portfolio_ml import portfolio_ml, cluster_profiles
from inti_intelligence.decision_intelligence import executive_actions
from inti_intelligence.sentiment_analysis import get_reviews_mock_data

csv_path = ROOT / 'data' / 'output' / 'catalog_enriched_latest.csv'
if not csv_path.exists():
    csv_path = ROOT / 'data' / 'snapshots' / 'snapshot_01_2026-08-24.csv'

catalog = pd.read_csv(csv_path)

print("=== CATALOG DATASET ===")
print(f"File: {csv_path.name}")
print(f"Total Rows (Products): {len(catalog)}")
print(f"Columns ({len(catalog.columns)}): {list(catalog.columns)}")
print("\nSample Products:")
cols_show = [c for c in ['product_id', 'name', 'category', 'color', 'price', 'original_price', 'discount_pct'] if c in catalog.columns]
print(catalog[cols_show].head(5).to_string())

print("\n=== COMMERCIAL SUMMARY ===")
cs = category_commercial_summary(catalog)
print(cs.to_string())

print("\n=== ASSORTMENT ARCHITECTURE ===")
ca = category_architecture(catalog)
print(ca.to_string())

print("\n=== PORTFOLIO ML CLUSTERS ===")
p_df = portfolio_ml(catalog)
cp = cluster_profiles(p_df)
print(cp.to_string())

print("\n=== EXECUTIVE ACTIONS ===")
ea = executive_actions(catalog)
print(ea[['priority', 'scope', 'headline', 'recommended_action']].head(5).to_string())
