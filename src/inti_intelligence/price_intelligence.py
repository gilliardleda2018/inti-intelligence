from __future__ import annotations
import pandas as pd


def build_price_metrics(df: pd.DataFrame) -> dict:
    d = df.copy()
    d['price'] = pd.to_numeric(d.get('price'), errors='coerce')
    d['original_price'] = pd.to_numeric(d.get('original_price'), errors='coerce')
    d['discount_pct'] = pd.to_numeric(d.get('discount_pct'), errors='coerce')
    priced = d[d['price'].notna() & (d['price'] > 0)].copy()
    discounted = priced[priced['original_price'].notna() & (priced['original_price'] > priced['price'])]
    return {
        'variants_total': int(len(d)),
        'priced_variants': int(len(priced)),
        'price_coverage_pct': round(100 * len(priced) / len(d), 2) if len(d) else 0.0,
        'median_price': round(float(priced['price'].median()), 2) if len(priced) else None,
        'mean_price': round(float(priced['price'].mean()), 2) if len(priced) else None,
        'min_price': round(float(priced['price'].min()), 2) if len(priced) else None,
        'max_price': round(float(priced['price'].max()), 2) if len(priced) else None,
        'discounted_variants': int(len(discounted)),
        'discounted_pct': round(100 * len(discounted) / len(priced), 2) if len(priced) else 0.0,
        'median_discount_pct': round(float(discounted['discount_pct'].median()), 2) if len(discounted) and discounted['discount_pct'].notna().any() else None,
        'mean_discount_pct': round(float(discounted['discount_pct'].mean()), 2) if len(discounted) and discounted['discount_pct'].notna().any() else None,
        'max_discount_pct': round(float(discounted['discount_pct'].max()), 2) if len(discounted) and discounted['discount_pct'].notna().any() else None,
        'high_confidence_pct': round(100 * (priced.get('price_confidence', pd.Series(index=priced.index, dtype='object')) == 'HIGH').mean(), 2) if len(priced) else 0.0,
    }


def category_price_summary(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d['price'] = pd.to_numeric(d.get('price'), errors='coerce')
    d['original_price'] = pd.to_numeric(d.get('original_price'), errors='coerce')
    d['discount_pct'] = pd.to_numeric(d.get('discount_pct'), errors='coerce')
    d = d[d['price'].notna() & (d['price'] > 0)]
    if d.empty:
        return pd.DataFrame(columns=['category','variants','median_price','mean_price','min_price','max_price','discounted_pct','median_discount_pct'])
    d['is_discounted'] = d['original_price'].notna() & (d['original_price'] > d['price'])
    rows=[]
    for cat,g in d.groupby(d['category'].fillna('Sem categoria')):
        disc=g[g['is_discounted']]
        rows.append({
            'category':cat,'variants':len(g),
            'median_price':round(g['price'].median(),2),'mean_price':round(g['price'].mean(),2),
            'min_price':round(g['price'].min(),2),'max_price':round(g['price'].max(),2),
            'discounted_pct':round(100*g['is_discounted'].mean(),2),
            'median_discount_pct':round(disc['discount_pct'].median(),2) if len(disc) and disc['discount_pct'].notna().any() else None,
        })
    return pd.DataFrame(rows).sort_values('median_price',ascending=False)
