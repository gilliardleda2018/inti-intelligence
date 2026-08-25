from pathlib import Path
import json
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from inti_intelligence.data_layer import load_catalog_bundle
from inti_intelligence.assortment_intelligence import (
    assortment_kpis, category_architecture, color_architecture,
    variant_density, size_coverage, opportunity_engine,
)

def main():
    bundle = load_catalog_bundle(ROOT)
    catalog = bundle.catalog.copy()
    out = ROOT / "data" / "output"
    out.mkdir(parents=True, exist_ok=True)

    kpis = assortment_kpis(catalog)
    cats = category_architecture(catalog)
    colors = color_architecture(catalog)
    density = variant_density(catalog)
    sizes = size_coverage(catalog)
    opps = opportunity_engine(catalog)

    (out / "assortment_kpis.json").write_text(json.dumps(kpis, ensure_ascii=False, indent=2), encoding="utf-8")
    cats.to_csv(out / "assortment_by_category.csv", index=False)
    colors.to_csv(out / "color_architecture.csv", index=False)
    density.to_csv(out / "variant_density.csv", index=False)
    sizes.to_csv(out / "size_coverage.csv", index=False)
    opps.to_csv(out / "merchandising_opportunities.csv", index=False)

    print("INTI Assortment & Merchandising Intelligence")
    print("-------------------------------------------")
    for k,v in kpis.items():
        print(f"{k}: {v}")
    print(f"opportunities: {len(opps)}")
    print(f"high_priority: {(opps['priority']=='HIGH').sum() if len(opps) else 0}")
    print(f"Output: {out}")

if __name__ == "__main__":
    main()
