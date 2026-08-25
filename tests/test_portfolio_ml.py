import pandas as pd
from inti_intelligence.portfolio_ml import portfolio_ml,similarity_neighbors,near_duplicate_radar,cluster_profiles
def sample():
    rows=[]
    for i in range(6):
        rows.append({"name":f"Vestido {i}","category":"Vestidos","color":"Preto","sizes":"36|38|40|42","price":1500+i*20,"original_price":1500+i*20,"discount_pct":0})
    for i in range(6):
        rows.append({"name":f"Biquini {i}","category":"Biquínis","color":"Azul","sizes":"P|M|G","price":120+i*3,"original_price":350,"discount_pct":65})
    return pd.DataFrame(rows)
def test_ml_space():
    df,k=portfolio_ml(sample())
    assert len(df)==12 and k["clusters"]>=2
    assert {"portfolio_cluster","ml_x","ml_y"}.issubset(df.columns)
def test_neighbors():
    n=similarity_neighbors(sample(),3)
    assert len(n)==36
    assert n["similarity_pct"].between(0,100).all()
def test_profiles():
    p=cluster_profiles(sample())
    assert p["items"].sum()==12
def test_duplicate_radar():
    d=near_duplicate_radar(sample(),80)
    assert isinstance(d,pd.DataFrame)
