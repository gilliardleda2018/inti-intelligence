from pathlib import Path
import sys, json

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from inti_intelligence.data_layer import load_catalog_bundle
from inti_intelligence.decision_intelligence import category_decision_map, decision_kpis, executive_actions

def main():
    bundle = load_catalog_bundle(ROOT)
    catalog = bundle.catalog.copy()
    out = ROOT / "data" / "output"
    out.mkdir(parents=True, exist_ok=True)

    m = category_decision_map(catalog)
    k = decision_kpis(catalog)
    a = executive_actions(catalog, top_n=12)

    m.to_csv(out / "category_decision_map.csv", index=False)
    a.to_csv(out / "executive_actions.csv", index=False)
    (out / "decision_kpis.json").write_text(json.dumps(k, ensure_ascii=False, indent=2), encoding="utf-8")

    print("INTI Decision Intelligence")
    print("--------------------------")
    for key, val in k.items():
        print(f"{key}: {val}")
    print(f"executive_actions: {len(a)}")
    print(f"Output: {out}")

if __name__ == "__main__":
    main()
