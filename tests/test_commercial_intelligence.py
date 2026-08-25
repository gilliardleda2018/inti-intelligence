import pandas as pd
from src.inti_intelligence.commercial_intelligence import commercial_kpis, category_commercial_summary, markdown_pressure_by_category, add_price_tiers


def sample():
    return pd.DataFrame([
        {'category':'Vestidos','price':1000,'original_price':1000,'discount_pct':0},
        {'category':'Vestidos','price':800,'original_price':1600,'discount_pct':50},
        {'category':'Biquínis','price':200,'original_price':500,'discount_pct':60},
        {'category':'Biquínis','price':250,'original_price':250,'discount_pct':0},
    ])


def test_commercial_kpis():
    k = commercial_kpis(sample())
    assert k['priced_variants'] == 4
    assert k['discounted_pct'] == 50.0
    assert k['median_price'] == 525.0


def test_category_summary_and_pressure():
    c = category_commercial_summary(sample())
    assert set(c['category']) == {'Vestidos','Biquínis'}
    p = markdown_pressure_by_category(sample())
    assert 'markdown_pressure_index' in p.columns


def test_price_tiers():
    d = add_price_tiers(sample())
    assert set(d['price_tier']).issubset({'ENTRY','CORE','UPPER','PREMIUM','UNPRICED'})
