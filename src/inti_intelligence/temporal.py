from __future__ import annotations
import pandas as pd
from pathlib import Path


def _norm_sizes(v):
    if pd.isna(v): return set()
    return {x.strip() for x in str(v).split('|') if x.strip()}


def compare_snapshots(old: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    old = old.copy(); new = new.copy()
    old['product_id'] = old['product_id'].astype(str); new['product_id'] = new['product_id'].astype(str)
    a = old.set_index('product_id'); b = new.set_index('product_id')
    events = []
    for pid in sorted(set(b.index)-set(a.index)):
        r = b.loc[pid]; events.append(dict(event_type='PRODUCT_ADDED', product_id=pid, name=r.get('name'), detail='Produto/variante apareceu no catálogo público'))
    for pid in sorted(set(a.index)-set(b.index)):
        r = a.loc[pid]; events.append(dict(event_type='PRODUCT_REMOVED', product_id=pid, name=r.get('name'), detail='Produto/variante deixou de aparecer no snapshot público'))
    for pid in sorted(set(a.index)&set(b.index)):
        x = a.loc[pid]; y = b.loc[pid]
        os, ns = _norm_sizes(x.get('sizes')), _norm_sizes(y.get('sizes'))
        for s in sorted(os-ns): events.append(dict(event_type='SIZE_DISAPPEARED', product_id=pid, name=y.get('name'), detail=f'Tamanho {s} deixou de aparecer na grade pública'))
        for s in sorted(ns-os): events.append(dict(event_type='SIZE_RETURNED', product_id=pid, name=y.get('name'), detail=f'Tamanho {s} apareceu/retornou na grade pública'))
    return pd.DataFrame(events, columns=['event_type','product_id','name','detail'])


def snapshots(path='data/snapshots', enriched=False):
    """Return raw catalog snapshots by default; enriched snapshots when requested."""
    p = Path(path)
    if enriched:
        return sorted(p.glob('snapshot_*_enriched.csv'))
    return sorted(f for f in p.glob('snapshot_*.csv') if not f.name.endswith('_enriched.csv'))
