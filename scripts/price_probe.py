from pathlib import Path
import sys,argparse,time,json
import pandas as pd,requests
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from inti_intelligence.price_parser import parse_price_html
ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=10);ap.add_argument('--timeout',type=int,default=20);args=ap.parse_args()
src=sorted((ROOT/'data'/'snapshots').glob('*.csv'))[-1];df=pd.read_csv(src).head(args.limit)
headers={'User-Agent':'Mozilla/5.0 (compatible; INTI-Intelligence-Research/0.3; public catalog; low-rate)'}
rows=[]
for i,r in df.iterrows():
    url=r['url'];print(f'[{len(rows)+1}/{len(df)}] {r["name"]}')
    try:
        resp=requests.get(url,headers=headers,timeout=args.timeout);resp.raise_for_status()
        pr=parse_price_html(resp.text)
        rows.append({'product_id':r['product_id'],'name':r['name'],'url':url,**pr.dict()})
    except Exception as e:rows.append({'product_id':r['product_id'],'name':r['name'],'url':url,'error':str(e)})
    time.sleep(1.0)
out=ROOT/'data'/'output'/'price_probe.csv';pd.DataFrame(rows).to_csv(out,index=False)
print(f'Output: {out}')
print(pd.DataFrame(rows)[['name','price','original_price','discount_pct','source','confidence']].to_string(index=False))
