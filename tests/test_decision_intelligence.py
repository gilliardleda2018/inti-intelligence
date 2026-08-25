import pandas as pd
from inti_intelligence.decision_intelligence import category_decision_map, decision_kpis, executive_actions

def sample():
    rows = []
    for i in range(8):
        rows.append({"name":f"Vestido {i}","category":"Vestidos","color":"Preto" if i%2==0 else "Vermelho","sizes":"36|38|40|42","price":1600+i*20,"discount_pct":0})
    for i in range(6):
        rows.append({"name":f"Biquíni {i}","category":"Biquínis","color":"Preto","sizes":"P|M|G","price":120,"discount_pct":60+i})
    for i in range(3):
        rows.append({"name":f"Blazer {i}","category":"Blazers","color":"Off White","sizes":"36|38|40|42","price":1800,"discount_pct":0})
    return pd.DataFrame(rows)

def test_map_has_scores():
    out = category_decision_map(sample())
    required = {"strategic_score","archetype","assortment_importance","price_position","markdown_pressure"}
    assert required.issubset(out.columns)
    assert out["strategic_score"].between(0,100).all()

def test_kpis():
    k = decision_kpis(sample())
    assert k["categories"] == 3
    assert k["top_strategic_category"] is not None

def test_actions():
    a = executive_actions(sample())
    assert len(a) >= 3
    assert {"priority","headline","recommended_action"}.issubset(a.columns)
