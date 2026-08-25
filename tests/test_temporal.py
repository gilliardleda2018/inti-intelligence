import sys,pandas as pd
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from inti_intelligence.temporal import compare_snapshots

def test_size_disappeared_and_returned():
    a=pd.DataFrame([{'product_id':1,'name':'X','sizes':'36|38|40','price':100,'original_price':None}])
    b=pd.DataFrame([{'product_id':1,'name':'X','sizes':'36|40|42','price':100,'original_price':None}])
    e=compare_snapshots(a,b)
    assert 'SIZE_DISAPPEARED' in set(e.event_type)
    assert 'SIZE_RETURNED' in set(e.event_type)
