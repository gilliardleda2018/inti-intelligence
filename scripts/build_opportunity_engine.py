from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from inti_intelligence.data_layer import load_catalog_bundle
from inti_intelligence.opportunity_engine import (
    calibrated_similarity,
    cluster_intelligence,
    opportunity_engine,
    optimization_kpis,
)


def main():
    catalog = load_catalog_bundle(ROOT).catalog.copy()
    output = ROOT / "data" / "output"
    output.mkdir(parents=True, exist_ok=True)

    similarity = calibrated_similarity(catalog)
    clusters = cluster_intelligence(catalog)
    opportunities = opportunity_engine(catalog)
    kpis = optimization_kpis(catalog)

    similarity.to_csv(output / "calibrated_similarity.csv", index=False)
    clusters.to_csv(output / "cluster_intelligence.csv", index=False)
    opportunities.to_csv(output / "portfolio_opportunities.csv", index=False)

    (output / "optimization_kpis.json").write_text(
        json.dumps(kpis, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("INTI Portfolio Optimization & Opportunity Engine")
    print("------------------------------------------------")
    for key, value in kpis.items():
        print(f"{key}: {value}")
    print(f"Output: {output}")


if __name__ == "__main__":
    main()
