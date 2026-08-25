from pathlib import Path
import sys,json,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from inti_intelligence.normalizer import normalize

snaps=sorted((ROOT/'data'/'snapshots').glob('*.csv'))
if not snaps:raise SystemExit('Nenhum snapshot em data/snapshots')
src=snaps[-1];df=pd.read_csv(src)
products,variants,sizes=normalize(df)
out=ROOT/'data'/'output';out.mkdir(parents=True,exist_ok=True)
products.to_csv(out/'products.csv',index=False)
variants.to_csv(out/'product_variants.csv',index=False)
sizes.to_csv(out/'variant_sizes.csv',index=False)
quality=[]
for c in df.columns:
    n=int(df[c].notna().sum()); rows=len(df); pct=round(n/rows*100,2) if rows else 0
    quality.append({'field':c,'rows':rows,'non_null':n,'missing':rows-n,'completeness_pct':pct,'trust':'GOOD' if pct>=95 else ('PARTIAL' if pct>0 else 'MISSING')})
pd.DataFrame(quality).to_csv(out/'data_quality_report.csv',index=False)
kpi={'snapshot_file':src.name,'snapshot_rows':len(df),'products_base':len(products),'variants':len(variants),'size_rows':len(sizes),'categories':int(df.category.nunique(dropna=True)),'colors':int(df.color.nunique(dropna=True)),'collections':int(df.collection.nunique(dropna=True)),'price_coverage_pct':round(df.price.notna().mean()*100,2),'image_coverage_pct':round(df.image_urls.notna().mean()*100,2)}
(out/'catalog_kpis.json').write_text(json.dumps(kpi,ensure_ascii=False,indent=2),encoding='utf-8')
print('INTI Intelligence Sprint 3 baseline')
for k,v in kpi.items():print(f'{k}: {v}')
