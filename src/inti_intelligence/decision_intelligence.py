from __future__ import annotations

import numpy as np
import pandas as pd

from .assortment_intelligence import category_architecture


def _num(s):
    return pd.to_numeric(s, errors="coerce")


def _pct_rank(series: pd.Series) -> pd.Series:
    s = _num(series)
    if s.notna().sum() == 0:
        return pd.Series(50.0, index=series.index)
    return (s.rank(method="average", pct=True) * 100).fillna(50.0)


def category_decision_map(catalog: pd.DataFrame) -> pd.DataFrame:
    cats = category_architecture(catalog).copy()
    if cats.empty:
        return cats

    cats["assortment_importance"] = _pct_rank(cats["assortment_share_pct"])
    cats["price_position"] = _pct_rank(cats["median_price"])
    cats["markdown_pressure"] = (
        0.6 * _pct_rank(cats["markdown_share_pct"].fillna(0)) +
        0.4 * _pct_rank(cats["median_discount_pct"].fillna(0))
    ).clip(0,100)
    cats["size_depth"] = _pct_rank(cats["median_sizes_per_variant"])
    cats["color_diversity"] = _pct_rank(cats["colors"])

    # Promotional exposure rewards both breadth of markdown and depth of markdown.
    cats["promotional_exposure"] = (
        0.55 * cats["markdown_pressure"] +
        0.45 * _pct_rank(cats["discounted_variants"].fillna(0))
    ).clip(0,100)

    # Strategic score is intentionally not a sales score.
    # It estimates strategic visibility/importance in the public assortment.
    cats["strategic_score"] = (
        0.30 * cats["assortment_importance"] +
        0.25 * cats["price_position"] +
        0.15 * cats["size_depth"] +
        0.15 * cats["color_diversity"] +
        0.15 * (100 - cats["promotional_exposure"])
    ).clip(0,100).round(1)

    def archetype(r):
        ai, pp, mp = r["assortment_importance"], r["price_position"], r["markdown_pressure"]
        if ai >= 70 and pp >= 70 and mp < 65:
            return "PREMIUM_CORE"
        if pp >= 75 and ai < 70 and mp < 65:
            return "NICHE_PREMIUM"
        if mp >= 75:
            return "PROMOTION_PRESSURE"
        if ai >= 70 and pp < 70:
            return "CORE_ASSORTMENT"
        if ai < 40 and pp < 40:
            return "LONG_TAIL"
        return "WATCHLIST"

    cats["archetype"] = cats.apply(archetype, axis=1)

    def recommendation(r):
        a = r["archetype"]
        if a == "PREMIUM_CORE":
            return "Proteger margem e percepção de valor; priorizar storytelling, disponibilidade de grade e monitoramento de ruptura."
        if a == "NICHE_PREMIUM":
            return "Tratar como nicho de alto valor; testar exposição seletiva, clienteling e cross-sell sem desconto indiscriminado."
        if a == "PROMOTION_PRESSURE":
            return "Investigar causa da pressão promocional antes de ampliar compras; monitorar profundidade de markdown e cobertura de grade."
        if a == "CORE_ASSORTMENT":
            return "Monitorar amplitude, diversidade e produtividade futura quando vendas internas estiverem disponíveis."
        if a == "LONG_TAIL":
            return "Revisar papel estratégico no mix e evitar complexidade excessiva sem evidência de contribuição."
        return "Manter em observação e buscar evidências adicionais de demanda, margem e comportamento temporal."

    cats["recommendation"] = cats.apply(recommendation, axis=1)
    return cats.sort_values(["strategic_score","category"], ascending=[False,True]).reset_index(drop=True)


def decision_kpis(catalog: pd.DataFrame) -> dict:
    m = category_decision_map(catalog)
    if m.empty:
        return {
            "categories":0,"premium_core":0,"promotion_pressure":0,
            "niche_premium":0,"watchlist":0,"top_strategic_category":None,
            "top_strategic_score":None
        }
    counts = m["archetype"].value_counts()
    top = m.iloc[0]
    return {
        "categories": int(len(m)),
        "premium_core": int(counts.get("PREMIUM_CORE",0)),
        "promotion_pressure": int(counts.get("PROMOTION_PRESSURE",0)),
        "niche_premium": int(counts.get("NICHE_PREMIUM",0)),
        "watchlist": int(counts.get("WATCHLIST",0)),
        "top_strategic_category": str(top["category"]),
        "top_strategic_score": float(top["strategic_score"]),
    }


def executive_actions(catalog: pd.DataFrame, top_n: int = 8) -> pd.DataFrame:
    m = category_decision_map(catalog)
    if m.empty:
        return pd.DataFrame(columns=["priority","category","archetype","headline","why","recommended_action","strategic_score"])

    rows = []
    for _, r in m.iterrows():
        arch = r["archetype"]
        if arch == "PREMIUM_CORE":
            priority = "HIGH"
            headline = f"{r['category']}: núcleo premium do sortimento"
        elif arch == "PROMOTION_PRESSURE":
            priority = "HIGH"
            headline = f"{r['category']}: pressão promocional requer investigação"
        elif arch == "NICHE_PREMIUM":
            priority = "MEDIUM"
            headline = f"{r['category']}: nicho de alto valor"
        elif arch == "CORE_ASSORTMENT":
            priority = "MEDIUM"
            headline = f"{r['category']}: categoria estrutural do mix"
        elif arch == "LONG_TAIL":
            priority = "LOW"
            headline = f"{r['category']}: cauda longa do sortimento"
        else:
            priority = "MEDIUM"
            headline = f"{r['category']}: categoria em observação"

        why = (
            f"Importância {r['assortment_importance']:.0f}/100 · "
            f"Preço {r['price_position']:.0f}/100 · "
            f"Markdown {r['markdown_pressure']:.0f}/100 · "
            f"Grade {r['size_depth']:.0f}/100 · "
            f"Cores {r['color_diversity']:.0f}/100"
        )
        rows.append({
            "priority": priority,
            "category": r["category"],
            "archetype": arch,
            "headline": headline,
            "why": why,
            "recommended_action": r["recommendation"],
            "strategic_score": r["strategic_score"],
        })

    out = pd.DataFrame(rows)
    p = {"HIGH":0,"MEDIUM":1,"LOW":2}
    out["_p"] = out["priority"].map(p).fillna(9)
    return out.sort_values(["_p","strategic_score"], ascending=[True,False]).drop(columns="_p").head(top_n).reset_index(drop=True)
