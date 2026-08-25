from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from inti_intelligence.price_parser import parse_price_html
from inti_intelligence.price_intelligence import build_price_metrics, category_price_summary

UA='Mozilla/5.0 (compatible; INTI-Intelligence-Research/1.0; public-catalog-analysis)'

def main():
    ap=argparse.ArgumentParser(description='Enrich INTI public catalog with public product prices.')
    ap.add_argument('--input',default=str(ROOT/'data'/'snapshots'/'snapshot_01_2026-08-24.csv'))
    ap.add_argument('--limit',type=int,default=None)
    ap.add_argument('--delay',type=float,default=1.0,help='Seconds between requests.')
    ap.add_argument('--timeout',type=float,default=20)
    ap.add_argument('--resume',action=argparse.BooleanOptionalAction,default=True)
    args=ap.parse_args()

    inp=Path(args.input)
    if not inp.exists(): raise SystemExit(f'Input not found: {inp}')
    outdir=ROOT/'data'/'output';outdir.mkdir(parents=True,exist_ok=True)
    checkpoint=outdir/'price_enrichment_checkpoint.csv'
    final=outdir/'catalog_enriched_latest.csv'
    failures=outdir/'price_enrichment_failures.csv'

    base=pd.read_csv(inp)
    if args.limit: base=base.head(args.limit).copy()
    done={}
    if args.resume and checkpoint.exists():
        cp=pd.read_csv(checkpoint)
        if 'product_id' in cp.columns:
            done={str(r.product_id):r._asdict() for r in cp.itertuples(index=False)}
            print(f'Resume: {len(done)} previously processed rows')

    from urllib3.util import Retry
    from requests.adapters import HTTPAdapter
    
    sess=requests.Session()
    sess.headers.update({'User-Agent':UA,'Accept-Language':'pt-BR,pt;q=0.9,en;q=0.7'})
    
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    sess.mount('http://', HTTPAdapter(max_retries=retries))
    sess.mount('https://', HTTPAdapter(max_retries=retries))
    
    rows=[];fails=[]
    total=len(base)
    for n,(_,r) in enumerate(base.iterrows(),1):
        pid=str(r.get('product_id',''))
        if pid in done:
            rows.append(done[pid]);continue
        url=str(r.get('url',''))
        print(f'[{n}/{total}] {r.get("name","")}')
        rec=r.to_dict();rec.update({'price':None,'original_price':None,'discount_pct':None,'price_source':None,'price_confidence':'NONE','price_http_status':None,'price_error':None})
        try:
            resp=sess.get(url,timeout=args.timeout)
            rec['price_http_status']=resp.status_code
            if resp.status_code == 403:
                print(f"  [Alerta] Acesso proibido (403) para {url}. O site pode estar bloqueando a requisição.")
            elif resp.status_code == 429:
                print(f"  [Alerta] Limite de requisições excedido (429) para {url}. Use um atraso maior (--delay).")
            resp.raise_for_status()
            p=parse_price_html(resp.text)
            rec.update({'price':p.price,'original_price':p.original_price,'discount_pct':p.discount_pct,'price_source':p.source,'price_confidence':p.confidence})
            if p.price is None:
                rec['price_error']='NO_PRICE_FOUND';fails.append({'product_id':pid,'name':r.get('name'),'url':url,'error':'NO_PRICE_FOUND'})
        except Exception as e:
            rec['price_error']=type(e).__name__+': '+str(e)[:250]
            fails.append({'product_id':pid,'name':r.get('name'),'url':url,'error':rec['price_error']})
        rows.append(rec)
        pd.DataFrame(rows).to_csv(checkpoint,index=False,encoding='utf-8-sig')
        if args.delay>0: time.sleep(args.delay)

    enriched=pd.DataFrame(rows)
    # preserve original order where possible
    if 'product_id' in enriched.columns:
        enriched['_pid']=enriched['product_id'].astype(str)
        order={str(x):i for i,x in enumerate(base['product_id'].astype(str))}
        enriched['_order']=enriched['_pid'].map(order).fillna(10**9)
        enriched=enriched.sort_values('_order').drop(columns=['_pid','_order'])
    enriched.to_csv(final,index=False,encoding='utf-8-sig')
    pd.DataFrame(fails).to_csv(failures,index=False,encoding='utf-8-sig')

    metrics=build_price_metrics(enriched)
    (outdir/'price_kpis.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
    category_price_summary(enriched).to_csv(outdir/'price_by_category.csv',index=False,encoding='utf-8-sig')

    discounted=enriched[pd.to_numeric(enriched['discount_pct'],errors='coerce').notna()].copy()
    discounted['discount_pct']=pd.to_numeric(discounted['discount_pct'],errors='coerce')
    discounted.sort_values('discount_pct',ascending=False).head(50).to_csv(outdir/'top_markdowns.csv',index=False,encoding='utf-8-sig')

    print('\nINTI Price Intelligence')
    print('-----------------------')
    for k,v in metrics.items(): print(f'{k}: {v}')
    print(f'Output: {final}')
    print(f'Failures: {len(fails)} -> {failures}')

if __name__=='__main__': main()
