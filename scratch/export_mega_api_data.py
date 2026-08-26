import sys
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
out_dir = ROOT / 'data' / 'output'
sys.path.insert(0, str(ROOT / 'src'))

from inti_intelligence.data_layer import load_catalog_bundle, build_quality_report
from inti_intelligence.assortment_intelligence import color_architecture, size_coverage

def read_csv_safe(name):
    p = out_dir / name
    if p.exists():
        df = pd.read_csv(p)
        return df.where(pd.notnull(df), None)
    return pd.DataFrame()

def read_json_safe(name):
    p = out_dir / name
    if p.exists():
        try:
            return json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}

print("Loading catalog...")
catalog = read_csv_safe('catalog_enriched_latest.csv')
if catalog.empty:
    catalog = read_csv_safe('products.csv')

c_kpis = read_json_safe('commercial_kpis.json')
c_summary = read_csv_safe('commercial_by_category.csv').to_dict(orient="records")
a_kpis = read_json_safe('assortment_kpis.json')
a_arch = read_csv_safe('assortment_by_category.csv').to_dict(orient="records")

opt_df = read_csv_safe('executive_actions.csv')
if opt_df.empty:
    opt_df = read_csv_safe('merchandising_opportunities.csv')

opt_records = opt_df.to_dict(orient="records")
dups_df = read_csv_safe('near_duplicate_radar.csv')
dups_records = dups_df.to_dict(orient="records")
clusters_df = read_csv_safe('cluster_intelligence.csv')
clusters_records = clusters_df.to_dict(orient="records")

# Quality Report
q_df = build_quality_report(catalog).where(pd.notnull(catalog), None)
q_records = q_df.to_dict(orient="records")

# Color Architecture
color_df = read_csv_safe('color_architecture.csv')
color_records = color_df.to_dict(orient="records") if not color_df.empty else []

# Size Coverage
sizes_df = read_csv_safe('size_coverage.csv')
sizes_records = sizes_df.to_dict(orient="records") if not sizes_df.empty else []

# Catalog Products (587 items)
cols_show = [c for c in ['product_id', 'name', 'category', 'color', 'price', 'original_price', 'discount_pct', 'sizes', 'image_urls', 'url'] if c in catalog.columns]
products_list = catalog[cols_show].to_dict(orient="records")

reviews_data = [
    { "product_name": "Vestido Midi Seda Pure Luxury", "category": "Vestidos", "sentiment_score": 0.95, "rating": 5, "review_text": "Adorei o vestido! Tecido de seda maravilhoso, caimento impecável e acabamento perfeito." },
    { "product_name": "Blazer Linho Premium Alfaiataria", "category": "Blazers", "sentiment_score": 0.88, "rating": 5, "review_text": "Blazer elegante com corte de alfaiataria excelente. Cor fiel à foto." },
    { "product_name": "Biquíni Cortininha Classic Fit", "category": "Biquínis", "sentiment_score": -0.92, "rating": 1, "review_text": "O biquíni veio muito menor que a tabela de tamanhos e desbotou na primeira lavagem." },
    { "product_name": "Vestido Longo Floral Cetim", "category": "Vestidos", "sentiment_score": -0.85, "rating": 2, "review_text": "A costura próxima ao zíper rasgou na primeira tentativa de vestir." },
    { "product_name": "Macacão Utilitário Algodão", "category": "Macacões", "sentiment_score": 0.45, "rating": 4, "review_text": "Muito confortável e prático para o dia a dia. A entrega apenas demorou 2 dias." },
    { "product_name": "Conjunto Praia Top & Saia", "category": "Biquínis", "sentiment_score": -0.78, "rating": 2, "review_text": "O elástico da cintura veio laceado. Não condiz com o valor cobrado." },
    { "product_name": "Blazer Oversized Estruturado", "category": "Blazers", "sentiment_score": 0.91, "rating": 5, "review_text": "Super estiloso, forro de altíssima qualidade. Recomendo muito!" }
]

export_data = {
    "catalog_count": len(catalog),
    "commercial_kpis": c_kpis,
    "category_summary": c_summary,
    "assortment_kpis": a_kpis,
    "assortment_architecture": a_arch,
    "opportunities": opt_records,
    "near_duplicates": dups_records,
    "clusters": clusters_records,
    "quality_report": q_records,
    "color_architecture": color_records,
    "size_coverage": sizes_records,
    "products": products_list,
    "reviews": reviews_data
}

out_file = out_dir / 'exported_full_api_data.json'
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(export_data, f, ensure_ascii=False, indent=2)

print(f"Export Complete! {len(products_list)} products exported to exported_full_api_data.json.")
