import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from inti_intelligence.commercial_temporal import (
    compare_commercial_snapshots, commercial_temporal_kpis
)


def _df(rows):
    return pd.DataFrame(rows)


def test_price_increase_and_decrease():
    old = _df([
        {'product_id': 1, 'name': 'A', 'price': 100, 'original_price': None, 'discount_pct': None},
        {'product_id': 2, 'name': 'B', 'price': 200, 'original_price': None, 'discount_pct': None},
    ])
    new = _df([
        {'product_id': 1, 'name': 'A', 'price': 120, 'original_price': None, 'discount_pct': None},
        {'product_id': 2, 'name': 'B', 'price': 180, 'original_price': None, 'discount_pct': None},
    ])
    e = compare_commercial_snapshots(old, new)
    assert 'PRICE_INCREASED' in set(e.event_type)
    assert 'PRICE_DECREASED' in set(e.event_type)


def test_markdown_lifecycle_and_depth():
    old = _df([
        {'product_id': 1, 'name': 'A', 'price': 100, 'original_price': None, 'discount_pct': None},
        {'product_id': 2, 'name': 'B', 'price': 80, 'original_price': 100, 'discount_pct': 20},
        {'product_id': 3, 'name': 'C', 'price': 70, 'original_price': 100, 'discount_pct': 30},
    ])
    new = _df([
        {'product_id': 1, 'name': 'A', 'price': 70, 'original_price': 100, 'discount_pct': 30},
        {'product_id': 2, 'name': 'B', 'price': 100, 'original_price': None, 'discount_pct': None},
        {'product_id': 3, 'name': 'C', 'price': 60, 'original_price': 100, 'discount_pct': 40},
    ])
    e = compare_commercial_snapshots(old, new)
    types = set(e.event_type)
    assert {'MARKDOWN_STARTED', 'ENTERED_SALE', 'MARKDOWN_ENDED', 'LEFT_SALE', 'MARKDOWN_DEEPENED'} <= types


def test_kpis_zero_events_for_stable_snapshots():
    a = _df([{'product_id': 1, 'name': 'A', 'price': 100, 'original_price': 200, 'discount_pct': 50}])
    e = compare_commercial_snapshots(a, a.copy())
    k = commercial_temporal_kpis(a, a.copy(), e)
    assert k['comparable_variants'] == 1
    assert k['commercial_events_total'] == 0
