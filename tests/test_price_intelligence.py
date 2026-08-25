import sys
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from inti_intelligence.price_intelligence import build_price_metrics

def test_metrics():
    d=pd.DataFrame({'price':[100,200,None],'original_price':[200,200,None],'discount_pct':[50,None,None],'price_confidence':['HIGH','HIGH','NONE']})
    m=build_price_metrics(d)
    assert m['priced_variants']==2
    assert m['price_coverage_pct']==66.67
    assert m['discounted_variants']==1
    assert m['median_price']==150.0
