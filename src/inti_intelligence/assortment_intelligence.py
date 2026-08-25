from __future__ import annotations

import math
import pandas as pd
import numpy as np


def _num(series):
    return pd.to_numeric(series, errors="coerce")


def _norm_0_100(series: pd.Series) -> pd.Series:
    s = _num(series)
    if s.notna().sum() == 0:
        return pd.Series(0.0, index=series.index)
    lo, hi = s.min(), s.max()
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return pd.Series(50.0, index=series.index)
    return ((s - lo) / (hi - lo) * 100).clip(0, 100)


def category_architecture(catalog: pd.DataFrame) -> pd.DataFrame:
    df = catalog.copy()
    if "category" not in df:
        df["category"] = "Sem categoria"
    df["category"] = df["category"].fillna("Sem categoria")
    counts = df.groupby("category", dropna=False).size().rename("variants").reset_index()
    total = max(len(df), 1)
    counts["assortment_share_pct"] = (counts["variants"] / total * 100).round(2)

    if "color" in df:
        colors = df.groupby("category")["color"].nunique(dropna=True).rename("colors")
        counts = counts.merge(colors, on="category", how="left")
    else:
        counts["colors"] = 0

    if "sizes" in df:
        def size_count(v):
            if pd.isna(v): return 0
            return len([x for x in str(v).split("|") if x.strip()])
        tmp = df[["category","sizes"]].copy()
        tmp["size_count"] = tmp["sizes"].apply(size_count)
        size_stats = tmp.groupby("category")["size_count"].agg(["median","mean"]).reset_index()
        size_stats.columns = ["category","median_sizes_per_variant","mean_sizes_per_variant"]
        counts = counts.merge(size_stats, on="category", how="left")
    else:
        counts["median_sizes_per_variant"] = 0
        counts["mean_sizes_per_variant"] = 0

    if "price" in df:
        df["price"] = _num(df["price"])
        price = df.groupby("category")["price"].agg(["median","mean","max","count"]).reset_index()
        price.columns = ["category","median_price","mean_price","max_price","priced_variants"]
        counts = counts.merge(price, on="category", how="left")
    else:
        for c in ["median_price","mean_price","max_price","priced_variants"]:
            counts[c] = np.nan

    if "discount_pct" in df:
        df["discount_pct"] = _num(df["discount_pct"])
        df["discounted"] = df["discount_pct"].fillna(0) > 0
        disc = df.groupby("category").agg(
            discounted_variants=("discounted","sum"),
            median_discount_pct=("discount_pct","median"),
        ).reset_index()
        counts = counts.merge(disc, on="category", how="left")
        counts["markdown_share_pct"] = (
            counts["discounted_variants"] / counts["variants"].replace(0, np.nan) * 100
        ).fillna(0).round(2)
    else:
        counts["discounted_variants"] = 0
        counts["median_discount_pct"] = np.nan
        counts["markdown_share_pct"] = 0.0

    return counts.sort_values(["variants","category"], ascending=[False, True]).reset_index(drop=True)


def color_architecture(catalog: pd.DataFrame) -> pd.DataFrame:
    df = catalog.copy()
    if "color" not in df:
        return pd.DataFrame(columns=["color","variants","share_pct"])
    colors = df["color"].fillna("Sem cor").value_counts().rename_axis("color").reset_index(name="variants")
    colors["share_pct"] = (colors["variants"] / max(len(df),1) * 100).round(2)
    return colors


def variant_density(catalog: pd.DataFrame) -> pd.DataFrame:
    df = catalog.copy()
    name_col = "base_name" if "base_name" in df.columns else ("name" if "name" in df.columns else "variant_name")
    if name_col not in df:
        return pd.DataFrame(columns=["product","variants","colors"])
    out = df.groupby(name_col).agg(
        variants=(name_col,"size"),
        colors=("color","nunique") if "color" in df else (name_col,"size"),
    ).reset_index().rename(columns={name_col:"product"})
    return out.sort_values(["variants","product"], ascending=[False, True]).reset_index(drop=True)


def size_coverage(catalog: pd.DataFrame) -> pd.DataFrame:
    df = catalog.copy()
    if "sizes" not in df:
        return pd.DataFrame(columns=["name","category","color","size_count","size_coverage_score"])
    def parse(v):
        if pd.isna(v): return []
        return [x.strip() for x in str(v).split("|") if x.strip()]
    df["size_count"] = df["sizes"].apply(lambda x: len(parse(x)))
    cat_med = df.groupby(df.get("category", pd.Series(["Sem categoria"]*len(df)))).size_count.transform("median")
    df["size_coverage_score"] = np.where(
        cat_med > 0,
        (df["size_count"] / cat_med * 100).clip(0, 150),
        0
    ).round(1)
    cols = [c for c in ["product_id","name","variant_name","category","color","sizes","size_count","size_coverage_score","url"] if c in df.columns]
    return df[cols].sort_values(["size_coverage_score","size_count"], ascending=[True, True]).reset_index(drop=True)


def assortment_kpis(catalog: pd.DataFrame) -> dict:
    cats = category_architecture(catalog)
    colors = color_architecture(catalog)
    vd = variant_density(catalog)
    sc = size_coverage(catalog)
    total = len(catalog)
    top_cat_share = float(cats.iloc[0]["assortment_share_pct"]) if len(cats) else 0.0
    top_color_share = float(colors.iloc[0]["share_pct"]) if len(colors) else 0.0
    hhi_cat = float(((cats["assortment_share_pct"]/100)**2).sum()) if len(cats) else 0.0
    hhi_color = float(((colors["share_pct"]/100)**2).sum()) if len(colors) else 0.0
    return {
        "variants_total": int(total),
        "categories": int(cats["category"].nunique()) if len(cats) else 0,
        "colors": int(colors["color"].nunique()) if len(colors) else 0,
        "top_category_share_pct": round(top_cat_share,2),
        "top_color_share_pct": round(top_color_share,2),
        "category_concentration_hhi": round(hhi_cat,4),
        "color_concentration_hhi": round(hhi_color,4),
        "median_variants_per_product": round(float(vd["variants"].median()),2) if len(vd) else 0.0,
        "median_sizes_per_variant": round(float(sc["size_count"].median()),2) if len(sc) else 0.0,
    }


def opportunity_engine(catalog: pd.DataFrame) -> pd.DataFrame:
    cats = category_architecture(catalog).copy()
    if cats.empty:
        return pd.DataFrame(columns=["priority","signal_type","category","headline","evidence","action","score"])

    cats["share_score"] = _norm_0_100(cats["assortment_share_pct"])
    cats["markdown_score"] = _norm_0_100(cats["markdown_share_pct"].fillna(0))
    cats["discount_depth_score"] = _norm_0_100(cats["median_discount_pct"].fillna(0))
    cats["price_score"] = _norm_0_100(cats["median_price"].fillna(cats["median_price"].median() if cats["median_price"].notna().any() else 0))
    cats["size_score"] = _norm_0_100(cats["median_sizes_per_variant"].fillna(0))

    signals = []
    overall_share_med = cats["assortment_share_pct"].median()
    md_med = cats["markdown_share_pct"].median()
    price_med = cats["median_price"].median() if cats["median_price"].notna().any() else np.nan
    size_med = cats["median_sizes_per_variant"].median()

    for _, r in cats.iterrows():
        cat = r["category"]
        # Markdown concentration
        if r["markdown_share_pct"] >= max(25, md_med * 1.35) and r.get("discounted_variants",0) >= 3:
            score = min(100, 0.55*r["markdown_score"] + 0.45*r["discount_depth_score"])
            signals.append({
                "priority": "HIGH" if score >= 70 else "MEDIUM",
                "signal_type": "MARKDOWN_CONCENTRATION",
                "category": cat,
                "headline": f"{cat}: pressão promocional acima do mix",
                "evidence": f"{r['markdown_share_pct']:.1f}% das variantes em markdown; profundidade mediana {r['median_discount_pct']:.1f}%.",
                "action": "Revisar ciclo da categoria, cobertura de grade, preço cheio e necessidade de novas compras antes de ampliar promoções.",
                "score": round(float(score),1),
            })
        # Premium concentration
        if pd.notna(price_med) and pd.notna(r["median_price"]) and r["median_price"] >= price_med*1.25 and r["variants"] >= 5:
            score = min(100, 50 + (r["median_price"]/price_med-1)*80)
            signals.append({
                "priority": "MEDIUM",
                "signal_type": "PREMIUM_CONCENTRATION",
                "category": cat,
                "headline": f"{cat}: concentração de ticket premium",
                "evidence": f"Preço mediano R$ {r['median_price']:.2f}, acima da mediana global por categoria.",
                "action": "Proteger percepção de valor, priorizar storytelling e evitar desconto indiscriminado em itens premium.",
                "score": round(float(score),1),
            })
        # Size depth
        if r["median_sizes_per_variant"] < max(2, size_med*0.7) and r["variants"] >= 5:
            score = min(100, 100 - r["size_score"])
            signals.append({
                "priority": "MEDIUM" if score < 75 else "HIGH",
                "signal_type": "SIZE_DEPTH_GAP",
                "category": cat,
                "headline": f"{cat}: grade mais estreita que o padrão do catálogo",
                "evidence": f"Mediana de {r['median_sizes_per_variant']:.1f} tamanhos por variante.",
                "action": "Verificar se a grade reduzida é intencional por modelagem ou representa oportunidade de ampliar cobertura.",
                "score": round(float(score),1),
            })
        # Assortment dominance
        if r["assortment_share_pct"] >= max(20, overall_share_med*3):
            score = min(100, 45 + r["assortment_share_pct"]*1.8)
            signals.append({
                "priority": "MEDIUM",
                "signal_type": "ASSORTMENT_CONCENTRATION",
                "category": cat,
                "headline": f"{cat}: forte concentração do sortimento",
                "evidence": f"{r['assortment_share_pct']:.1f}% de todas as variantes públicas.",
                "action": "Avaliar se a concentração reflete estratégia de coleção ou dependência excessiva de uma categoria.",
                "score": round(float(score),1),
            })

    out = pd.DataFrame(signals)
    if out.empty:
        return pd.DataFrame(columns=["priority","signal_type","category","headline","evidence","action","score"])
    order = {"HIGH":0,"MEDIUM":1,"LOW":2}
    out["_p"] = out["priority"].map(order).fillna(9)
    return out.sort_values(["_p","score"], ascending=[True,False]).drop(columns="_p").reset_index(drop=True)
