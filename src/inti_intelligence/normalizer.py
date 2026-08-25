from __future__ import annotations
import re
import pandas as pd
import numpy as np

KNOWN_SIZES={"PP","P","M","G","GG","U","34","36","38","40","42","44","46","48"}

def _clean_text(v):
    if pd.isna(v): return None
    s=re.sub(r"\s+"," ",str(v)).strip()
    return s or None

def _split_pipe(v):
    if pd.isna(v): return []
    return [x.strip() for x in str(v).split('|') if x.strip()]

def _base_name(name,color):
    n=_clean_text(name) or ''
    c=_clean_text(color)
    if c and n.lower().endswith(c.lower()):
        n=n[:-len(c)].strip(' -–—/')
    return n or (_clean_text(name) or '')

def normalize(df:pd.DataFrame):
    d=df.copy()
    for col in ['name','collection','category','color','description','composition','image_urls','url']:
        if col in d:d[col]=d[col].map(_clean_text)
    d['product_base']=[_base_name(n,c) for n,c in zip(d['name'],d.get('color'))]
    d['variant_key']=d['product_id'].astype(str)
    d['size_list']=d['sizes'].map(_split_pipe)
    d['price_quality']=np.where(d['price'].notna(),'observed','missing')
    d['availability_quality']='untrusted_legacy_parser'
    prod=(d.groupby(['product_base','collection','category'],dropna=False)
          .agg(variant_count=('variant_key','nunique'),colors=('color',lambda s:'|'.join(sorted({x for x in s.dropna() if x}))),public_pages=('url','nunique'))
          .reset_index())
    prod.insert(0,'product_key',range(1,len(prod)+1))
    mp=prod[['product_key','product_base','collection','category']]
    variants=d.merge(mp,on=['product_base','collection','category'],how='left')
    variants=variants.rename(columns={'name':'variant_name','product_id':'variant_id'})
    size_rows=[]
    for r in variants.itertuples(index=False):
        for size in _split_pipe(r.sizes):
            size_rows.append({'product_key':r.product_key,'variant_id':r.variant_id,'product_base':r.product_base,'variant_name':r.variant_name,'color':r.color,'size':size,'size_known':size.upper() in KNOWN_SIZES,'collection':r.collection,'category':r.category,'url':r.url,'image_urls':r.image_urls,'snapshot_collected_at':r.collected_at,'availability':None,'availability_quality':'unknown_not_observed_per_size'})
    return prod,variants,pd.DataFrame(size_rows)
