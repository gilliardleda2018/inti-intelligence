from __future__ import annotations
import numpy as np
import pandas as pd


def _numeric(d: pd.DataFrame) -> pd.DataFrame:
    x = d.copy()
    for c in ('price', 'original_price', 'discount_pct'):
        x[c] = pd.to_numeric(x.get(c), errors='coerce')
    x['category'] = x.get('category', pd.Series(index=x.index, dtype='object')).fillna('Sem categoria')
    x['is_discounted'] = x['original_price'].notna() & x['price'].notna() & (x['original_price'] > x['price'])
    return x


def commercial_kpis(df: pd.DataFrame) -> dict:
    d = _numeric(df)
    priced = d[d['price'].notna() & (d['price'] > 0)].copy()
    if priced.empty:
        return {
            'priced_variants': 0, 'price_coverage_pct': 0.0, 'median_price': None,
            'q75_price': None, 'premium_threshold': None, 'discounted_pct': 0.0,
            'median_discount_pct': None, 'promotion_concentration_top_category_pct': None,
        }
    disc = priced[priced['is_discounted']]
    threshold = float(priced['price'].quantile(.75))
    promo_counts = disc['category'].value_counts()
    promo_conc = (100 * promo_counts.iloc[0] / len(disc)) if len(disc) and len(promo_counts) else None
    return {
        'priced_variants': int(len(priced)),
        'price_coverage_pct': round(100 * len(priced) / len(d), 2) if len(d) else 0.0,
        'median_price': round(float(priced['price'].median()), 2),
        'q75_price': round(threshold, 2),
        'premium_threshold': round(threshold, 2),
        'discounted_pct': round(100 * priced['is_discounted'].mean(), 2),
        'median_discount_pct': round(float(disc['discount_pct'].median()), 2) if len(disc) and disc['discount_pct'].notna().any() else None,
        'promotion_concentration_top_category_pct': round(float(promo_conc), 2) if promo_conc is not None else None,
    }


def category_commercial_summary(df: pd.DataFrame) -> pd.DataFrame:
    d = _numeric(df)
    d = d[d['price'].notna() & (d['price'] > 0)].copy()
    if d.empty:
        return pd.DataFrame()
    global_median = float(d['price'].median())
    rows = []
    for cat, g in d.groupby('category', dropna=False):
        disc = g[g['is_discounted']]
        med = float(g['price'].median())
        q25 = float(g['price'].quantile(.25))
        q75 = float(g['price'].quantile(.75))
        rows.append({
            'category': cat,
            'variants': int(len(g)),
            'median_price': round(med, 2),
            'q25_price': round(q25, 2),
            'q75_price': round(q75, 2),
            'max_price': round(float(g['price'].max()), 2),
            'discounted_variants': int(len(disc)),
            'discounted_pct': round(100 * g['is_discounted'].mean(), 2),
            'median_discount_pct': round(float(disc['discount_pct'].median()), 2) if len(disc) and disc['discount_pct'].notna().any() else None,
            'price_position_index': round(100 * med / global_median, 1) if global_median else None,
        })
    result = pd.DataFrame(rows).sort_values('median_price', ascending=False)
    result['category_price_tier'] = pd.cut(
        result['price_position_index'], bins=[-np.inf, 80, 120, np.inf],
        labels=['ACCESS', 'CORE', 'PREMIUM']
    ).astype(str)
    return result


def add_price_tiers(df: pd.DataFrame) -> pd.DataFrame:
    d = _numeric(df)
    priced = d[d['price'].notna() & (d['price'] > 0)].copy()
    if priced.empty:
        d['price_tier'] = 'UNPRICED'
        return d
    q25, q50, q75 = priced['price'].quantile([.25, .5, .75])
    def tier(v):
        if pd.isna(v): return 'UNPRICED'
        if v <= q25: return 'ENTRY'
        if v <= q50: return 'CORE'
        if v <= q75: return 'UPPER'
        return 'PREMIUM'
    d['price_tier'] = d['price'].apply(tier)
    return d


def markdown_pressure_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Transparent heuristic, not ML.

    Score 0-100 combines breadth of markdown (share discounted) and depth
    (median discount) with equal weights.
    """
    c = category_commercial_summary(df)
    if c.empty:
        return c
    x = c.copy()
    depth = x['median_discount_pct'].fillna(0).clip(0, 100)
    breadth = x['discounted_pct'].fillna(0).clip(0, 100)
    x['markdown_pressure_index'] = (0.5 * breadth + 0.5 * depth).round(1)
    return x.sort_values('markdown_pressure_index', ascending=False)
