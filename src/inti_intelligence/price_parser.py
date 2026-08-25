from __future__ import annotations
import json,re
from dataclasses import dataclass,asdict
from bs4 import BeautifulSoup

BRL_RE=re.compile(r"R\$\s*([0-9\.]+,[0-9]{2})")

def brl_to_float(v):
    if v is None:return None
    if isinstance(v,(int,float)):return float(v)
    s=str(v).strip().replace('R$','').strip()
    if ',' in s: s=s.replace('.','').replace(',','.')
    try:return float(s)
    except:return None

@dataclass
class PriceResult:
    price: float|None=None
    original_price: float|None=None
    discount_pct: float|None=None
    source: str|None=None
    confidence: str='NONE'
    raw_candidates: list|None=None
    def dict(self):return asdict(self)

def _walk_json(obj,out):
    if isinstance(obj,dict):
        typ=str(obj.get('@type','')).lower()
        if typ in ('product','offer','aggregateoffer') or 'offers' in obj:
            for k in ('price','lowPrice','highPrice'):
                if k in obj:
                    x=brl_to_float(obj.get(k))
                    if x: out.append(('jsonld:'+k,x))
            if 'offers' in obj:_walk_json(obj['offers'],out)
        for v in obj.values():
            if isinstance(v,(dict,list)):_walk_json(v,out)
    elif isinstance(obj,list):
        for v in obj:_walk_json(v,out)

def parse_price_html(html:str)->PriceResult:
    soup=BeautifulSoup(html,'lxml')
    cand=[]
    # JSON-LD: preferred structured source
    for tag in soup.find_all('script',attrs={'type':'application/ld+json'}):
        try:_walk_json(json.loads(tag.string or tag.get_text()),cand)
        except Exception:pass
    # OpenGraph / product meta
    for key in ['product:price:amount','og:price:amount','price','twitter:data1']:
        tag=soup.find('meta',attrs={'property':key}) or soup.find('meta',attrs={'name':key})
        if tag and tag.get('content'):
            x=brl_to_float(tag['content'])
            if x:cand.append(('meta:'+key,x))
    # data attributes commonly used by storefronts
    for tag in soup.find_all(attrs=True):
        for a in ('data-price','data-sale-price','data-compare-price','data-original-price'):
            if tag.has_attr(a):
                x=brl_to_float(tag.get(a))
                if x:cand.append((a,x))
    # visible R$ fallback; prioritize product area before whole page
    areas=[]
    for sel in ['main','.product','.product-info','.product__info','.product-info__content','body']:
        try:
            el=soup.select_one(sel)
            if el:areas.append(el.get_text(' ',strip=True))
        except Exception:pass
    seen_text=set()
    for text in areas:
        if text in seen_text:continue
        seen_text.add(text)
        for m in BRL_RE.finditer(text):
            x=brl_to_float(m.group(0))
            if x:cand.append(('visible_text',x))
    # de-duplicate preserving order
    uniq=[];seen=set()
    for s,v in cand:
        key=(s,round(v,2))
        if key not in seen: seen.add(key);uniq.append((s,v))
    if not uniq:return PriceResult(raw_candidates=[])
    structured=[x for x in uniq if x[0].startswith(('jsonld:','meta:','data-'))]
    chosen=structured or uniq
    vals=[]
    for s,v in chosen:
        if v not in vals:vals.append(v)
    # If two values are present, larger is usually compare/original price and smaller current price.
    price=min(vals) if len(vals)>=2 else vals[0]
    original=max(vals) if len(vals)>=2 and max(vals)>price else None
    disc=round((1-price/original)*100,2) if original and original>0 else None
    conf='HIGH' if structured else 'MEDIUM'
    src=chosen[0][0]
    return PriceResult(price,original,disc,src,conf,[{'source':s,'value':v} for s,v in uniq])
