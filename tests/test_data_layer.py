import pandas as pd
from src.inti_intelligence.data_layer import build_quality_report


def test_enriched_price_quality_is_not_missing():
    d = pd.DataFrame({
        'product_id':[1,2], 'name':['A','B'], 'url':['u','v'], 'collection':['C','C'],
        'category':['X','X'], 'color':['P','Q'], 'price':[100,200],
        'original_price':[100,300], 'discount_pct':[0,33.3], 'sizes':['P|M','M|G'],
        'price_confidence':['HIGH','HIGH']
    })
    q = build_quality_report(d)
    price = q[q.field == 'price'].iloc[0]
    assert price.completeness_pct == 100.0
    assert price.trust == 'GOOD'
