import pandas as pd
from inti_intelligence.product_intelligence import product_intelligence,product_kpis,product_opportunities
def sample():
    return pd.DataFrame([
      {"name":"A","category":"Vestidos","color":"Preto","sizes":"36|38|40|42","price":1500,"discount_pct":0},
      {"name":"B","category":"Vestidos","color":"Preto","sizes":"36|38|40|42","price":1400,"discount_pct":0},
      {"name":"C","category":"Vestidos","color":"Preto","sizes":"36|38|40|42","price":1450,"discount_pct":60},
      {"name":"D","category":"Biquínis","color":"Azul","sizes":"P|M|G","price":120,"discount_pct":65},
      {"name":"E","category":"Biquínis","color":"Azul","sizes":"P|M|G","price":250,"discount_pct":0},
    ])
def test_product_scores():
    p=product_intelligence(sample())
    assert p["product_strategic_score"].between(0,100).all()
    assert {"product_role","redundancy_watch","recommended_action"}.issubset(p.columns)
def test_product_kpis():
    assert product_kpis(sample())["products_analyzed"]==5
def test_product_opportunities():
    assert len(product_opportunities(sample()))==5
