import pandas as pd
from inti_intelligence.assortment_intelligence import (
    category_architecture, assortment_kpis, opportunity_engine, size_coverage
)

def sample():
    return pd.DataFrame([
        {"name":"A Preto","category":"Biquínis","color":"Preto","sizes":"P|M|G","price":120,"discount_pct":65},
        {"name":"A Pérola","category":"Biquínis","color":"Pérola","sizes":"P|M|G","price":120,"discount_pct":65},
        {"name":"B Preto","category":"Biquínis","color":"Preto","sizes":"P|M","price":130,"discount_pct":60},
        {"name":"C Preto","category":"Vestidos","color":"Preto","sizes":"36|38|40|42","price":1200,"discount_pct":0},
        {"name":"D Off","category":"Vestidos","color":"Off White","sizes":"36|38|40|42","price":1500,"discount_pct":0},
        {"name":"E Vermelho","category":"Vestidos","color":"Vermelho","sizes":"36|38|40|42","price":1800,"discount_pct":0},
    ])

def test_category_architecture():
    out = category_architecture(sample())
    assert out["variants"].sum() == 6
    assert set(out["category"]) == {"Biquínis","Vestidos"}

def test_kpis():
    k = assortment_kpis(sample())
    assert k["variants_total"] == 6
    assert k["categories"] == 2
    assert k["colors"] >= 3

def test_opportunities():
    o = opportunity_engine(sample())
    assert len(o) >= 1
    assert "MARKDOWN_CONCENTRATION" in set(o["signal_type"])

def test_size_coverage():
    s = size_coverage(sample())
    assert "size_coverage_score" in s.columns
    assert len(s) == 6
