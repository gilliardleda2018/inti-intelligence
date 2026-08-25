from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from inti_intelligence.data_layer import load_catalog_bundle
from inti_intelligence.product_intelligence import product_intelligence,product_kpis,product_opportunities
def main():
    catalog=load_catalog_bundle(ROOT).catalog.copy()
    out=ROOT/"data"/"output"; out.mkdir(parents=True,exist_ok=True)
    p=product_intelligence(catalog); k=product_kpis(catalog); o=product_opportunities(catalog)
    p.to_csv(out/"product_intelligence.csv",index=False)
    o.to_csv(out/"product_opportunities.csv",index=False)
    (out/"product_kpis.json").write_text(json.dumps(k,ensure_ascii=False,indent=2),encoding="utf-8")
    print("INTI Product Intelligence")
    print("-------------------------")
    for a,b in k.items(): print(f"{a}: {b}")
    print(f"opportunities: {len(o)}")
    print(f"Output: {out}")
if __name__=="__main__": main()
