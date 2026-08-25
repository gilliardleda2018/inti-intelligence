from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from inti_intelligence.data_layer import load_catalog_bundle
from inti_intelligence.portfolio_ml import portfolio_ml,similarity_neighbors,near_duplicate_radar,cluster_profiles,white_space_candidates
def main():
    catalog=load_catalog_bundle(ROOT).catalog.copy()
    out=ROOT/"data"/"output"; out.mkdir(parents=True,exist_ok=True)
    space,kpis=portfolio_ml(catalog)
    neigh=similarity_neighbors(catalog)
    dup=near_duplicate_radar(catalog)
    prof=cluster_profiles(catalog)
    white=white_space_candidates(catalog)
    space.to_csv(out/"product_ml_space.csv",index=False)
    neigh.to_csv(out/"product_neighbors.csv",index=False)
    dup.to_csv(out/"near_duplicate_radar.csv",index=False)
    prof.to_csv(out/"portfolio_clusters.csv",index=False)
    white.to_csv(out/"white_space_candidates.csv",index=False)
    (out/"portfolio_ml_kpis.json").write_text(json.dumps(kpis,ensure_ascii=False,indent=2),encoding="utf-8")
    print("INTI Product Similarity & Portfolio ML")
    print("--------------------------------------")
    for a,b in kpis.items(): print(f"{a}: {b}")
    print(f"neighbor_links: {len(neigh)}")
    print(f"near_duplicate_pairs: {len(dup)}")
    print(f"sparse_zones: {len(white)}")
    print(f"Output: {out}")
if __name__=="__main__": main()
