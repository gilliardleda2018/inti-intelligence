from __future__ import annotations
import numpy as np
import pandas as pd

def _num(s): return pd.to_numeric(s, errors="coerce")
def _rank(s):
    x=_num(s)
    return (x.rank(method="average",pct=True)*100).fillna(50.0)

def _size_count(v):
    if pd.isna(v): return 0
    return len([x for x in str(v).replace(",","|").split("|") if x.strip()])

def product_intelligence(catalog: pd.DataFrame) -> pd.DataFrame:
    df=catalog.copy()
    if df.empty: return df
    for c in ["category","color","name"]:
        if c not in df: df[c]="Unknown"
        df[c]=df[c].fillna("Unknown").astype(str)
    if "price" not in df: df["price"]=np.nan
    if "discount_pct" not in df: df["discount_pct"]=0
    if "sizes" not in df: df["sizes"]=""

    df["price"]=_num(df["price"])
    df["discount_pct"]=_num(df["discount_pct"]).fillna(0)
    df["size_count"]=df["sizes"].apply(_size_count)

    # Relative positions are computed inside category where possible.
    df["price_position"]=df.groupby("category")["price"].transform(_rank)
    df["size_depth"]=df.groupby("category")["size_count"].transform(_rank)
    df["markdown_pressure"]=df.groupby("category")["discount_pct"].transform(_rank)

    color_freq=df.groupby(["category","color"])["name"].transform("count")
    df["color_support"]=_rank(color_freq)

    # Structural product score only: no sales/demand inference.
    df["product_strategic_score"]=(
        .35*df["price_position"]+
        .25*df["size_depth"]+
        .20*df["color_support"]+
        .20*(100-df["markdown_pressure"])
    ).clip(0,100).round(1)

    def role(r):
        if r["markdown_pressure"]>=85 and r["discount_pct"]>0: return "MARKDOWN_WATCH"
        if r["price_position"]>=85 and r["product_strategic_score"]>=65: return "PREMIUM_ANCHOR"
        if r["product_strategic_score"]>=75 and r["size_depth"]>=60: return "HERO_CANDIDATE"
        if r["product_strategic_score"]>=55: return "ASSORTMENT_SUPPORT"
        return "LONG_TAIL_WATCH"
    df["product_role"]=df.apply(role,axis=1)

    # Explainable near-duplicate signature; signals overlap, not cannibalization.
    price_band=(df["price"].fillna(-1)/100).round().astype(int)
    df["_signature"]=df["category"]+"|"+df["color"]+"|"+df["size_count"].astype(str)+"|"+price_band.astype(str)
    df["similar_products"]=df.groupby("_signature")["name"].transform("count")-1
    df["redundancy_watch"]=df["similar_products"]>=2

    def action(r):
        if r["product_role"]=="MARKDOWN_WATCH":
            return "Investigar motivo do markdown e comparar com produtos semelhantes antes de ampliar exposição ou recompra."
        if r["redundancy_watch"]:
            return "Revisar sobreposição estrutural com itens semelhantes; validar diferenciação com vendas e margem quando disponíveis."
        if r["product_role"]=="PREMIUM_ANCHOR":
            return "Proteger percepção de valor, conteúdo e disponibilidade de grade; candidato a âncora premium."
        if r["product_role"]=="HERO_CANDIDATE":
            return "Candidato estrutural a produto-herói; validar com vendas, conversão, margem e estoque antes de confirmar."
        if r["product_role"]=="ASSORTMENT_SUPPORT":
            return "Manter como suporte de sortimento e acompanhar sinais temporais."
        return "Monitorar papel no mix e buscar evidências internas de produtividade."
    df["recommended_action"]=df.apply(action,axis=1)
    return df.drop(columns=["_signature"]).sort_values("product_strategic_score",ascending=False).reset_index(drop=True)

def product_kpis(catalog):
    p=product_intelligence(catalog)
    vc=p["product_role"].value_counts() if not p.empty else {}
    return {
        "products_analyzed":int(len(p)),
        "hero_candidates":int(vc.get("HERO_CANDIDATE",0)),
        "premium_anchors":int(vc.get("PREMIUM_ANCHOR",0)),
        "markdown_watch":int(vc.get("MARKDOWN_WATCH",0)),
        "redundancy_watch":int(p["redundancy_watch"].sum()) if not p.empty else 0,
        "top_product":None if p.empty else str(p.iloc[0]["name"]),
        "top_score":None if p.empty else float(p.iloc[0]["product_strategic_score"])
    }

def product_opportunities(catalog, top_n=30):
    p=product_intelligence(catalog)
    if p.empty: return p
    priority=np.where(p["product_role"].isin(["MARKDOWN_WATCH","HERO_CANDIDATE"]),"HIGH",
             np.where((p["product_role"]=="PREMIUM_ANCHOR")|p["redundancy_watch"],"MEDIUM","LOW"))
    out=p.assign(priority=priority)
    cols=["priority","name","category","color","product_role","product_strategic_score",
          "price","discount_pct","size_count","similar_products","redundancy_watch","recommended_action"]
    order={"HIGH":0,"MEDIUM":1,"LOW":2}
    out["_p"]=out["priority"].map(order)
    return out.sort_values(["_p","product_strategic_score"],ascending=[True,False])[cols].head(top_n).reset_index(drop=True)
