from __future__ import annotations
import numpy as np
import pandas as pd

from .product_intelligence import product_intelligence
from .portfolio_ml import portfolio_ml, cluster_profiles, similarity_neighbors


def _clip(value):
    return float(np.clip(value, 0, 100))


def _evidence_level(score, evidence_count):
    if evidence_count >= 4 and score >= 75:
        return "STRONG"
    if evidence_count >= 3 and score >= 55:
        return "MODERATE"
    return "EXPLORATORY"


def calibrated_similarity(catalog: pd.DataFrame, threshold: float = 94.0) -> pd.DataFrame:
    products = product_intelligence(catalog)
    neighbors = similarity_neighbors(catalog, 5)

    if neighbors.empty:
        return neighbors

    lookup = products.set_index("name", drop=False)
    rows = []

    for _, row in neighbors.iterrows():
        if row["product"] not in lookup.index or row["neighbor"] not in lookup.index:
            continue

        a = lookup.loc[row["product"]]
        b = lookup.loc[row["neighbor"]]

        if isinstance(a, pd.DataFrame):
            a = a.iloc[0]
        if isinstance(b, pd.DataFrame):
            b = b.iloc[0]

        same_category = str(a.get("category")) == str(b.get("category"))
        same_color = str(a.get("color")) == str(b.get("color"))
        same_sizes = str(a.get("sizes", "")) == str(b.get("sizes", ""))

        pa = pd.to_numeric(pd.Series([a.get("price")]), errors="coerce").iloc[0]
        pb = pd.to_numeric(pd.Series([b.get("price")]), errors="coerce").iloc[0]

        price_gap = np.nan
        if pd.notna(pa) and pd.notna(pb) and max(pa, pb) > 0:
            price_gap = abs(pa - pb) / max(pa, pb) * 100

        raw = float(row["similarity_pct"])
        calibrated = raw

        if not same_category:
            calibrated -= 12
        if pd.notna(price_gap):
            calibrated -= min(15, price_gap * 0.25)
        if same_sizes:
            calibrated += 2
        if same_color:
            calibrated += 1

        calibrated = _clip(calibrated)

        signal = (
            "VARIANT_LIKE"
            if same_category and same_sizes and pd.notna(price_gap) and price_gap <= 8
            else "STRUCTURAL_NEIGHBOR"
        )

        rows.append({
            **row.to_dict(),
            "calibrated_similarity_pct": round(calibrated, 2),
            "same_category": same_category,
            "same_color": same_color,
            "same_sizes": same_sizes,
            "price_gap_pct": None if pd.isna(price_gap) else round(float(price_gap), 2),
            "similarity_signal": signal,
        })

    out = pd.DataFrame(rows)
    if out.empty:
        return out

    out = out[out["calibrated_similarity_pct"] >= threshold].copy()
    if out.empty:
        return out

    out["_pair"] = out.apply(
        lambda x: "||".join(sorted([str(x["product"]), str(x["neighbor"])])),
        axis=1,
    )

    return (
        out.sort_values("calibrated_similarity_pct", ascending=False)
        .drop_duplicates("_pair")
        .drop(columns="_pair")
        .reset_index(drop=True)
    )


def cluster_intelligence(catalog: pd.DataFrame) -> pd.DataFrame:
    space, _ = portfolio_ml(catalog)
    profiles = cluster_profiles(catalog)

    if profiles.empty:
        return profiles

    total = len(space)
    median_price = pd.to_numeric(space["price"], errors="coerce").median()
    median_discount = pd.to_numeric(space["discount_pct"], errors="coerce").median()

    rows = []

    for _, row in profiles.iterrows():
        cluster_id = int(row["portfolio_cluster"])
        members = space[space["portfolio_cluster"] == cluster_id]

        density = _clip(len(members) / max(1, total) * 300)

        row_median_price = pd.to_numeric(
            pd.Series([row.get("median_price")]), errors="coerce"
        ).iloc[0]
        row_mean_discount = pd.to_numeric(
            pd.Series([row.get("mean_discount_pct")]), errors="coerce"
        ).iloc[0]

        premium = _clip(
            (float(row_median_price) / max(1, float(median_price)))
            * 50
        ) if pd.notna(row_median_price) and pd.notna(median_price) else 0.0

        discount_reference = (
            float(median_discount)
            if pd.notna(median_discount) and median_discount > 0
            else 20.0
        )

        markdown = _clip(
            (float(row_mean_discount) / discount_reference) * 35
        ) if pd.notna(row_mean_discount) else 0.0

        if len(members) <= max(5, int(total * 0.05)):
            archetype = "SPARSE_ZONE"
        elif markdown >= 70:
            archetype = "PROMOTIONAL_DENSITY"
        elif premium >= 75:
            archetype = "PREMIUM_DENSITY"
        elif density >= 70:
            archetype = "CORE_DENSITY"
        else:
            archetype = "BALANCED_CLUSTER"

        rows.append({
            **row.to_dict(),
            "cluster_archetype": archetype,
            "density_score": round(density, 1),
            "premium_score": round(premium, 1),
            "markdown_score": round(markdown, 1),
        })

    return pd.DataFrame(rows)


def opportunity_engine(catalog: pd.DataFrame) -> pd.DataFrame:
    products = product_intelligence(catalog)
    clusters = cluster_intelligence(catalog)
    rows = []

    for category, group in products.groupby("category", dropna=False):
        category = str(category)
        count = len(group)
        markdown_count = int((group["product_role"] == "MARKDOWN_WATCH").sum())
        hero_count = int((group["product_role"] == "HERO_CANDIDATE").sum())
        anchor_count = int((group["product_role"] == "PREMIUM_ANCHOR").sum())
        avg_score = float(group["product_strategic_score"].mean())

        evidence_count = sum([
            count >= 10,
            markdown_count >= 3,
            hero_count >= 1,
            anchor_count >= 3,
        ])

        score = _clip(
            avg_score * 0.55
            + min(100, markdown_count / max(1, count) * 300) * 0.25
            + min(100, (hero_count + anchor_count) * 12) * 0.20
        )

        if markdown_count >= 3:
            headline = f"{category}: concentração de markdown requer investigação"
            action = (
                "Revisar arquitetura promocional, diferenciação e papel dos itens; "
                "validar com margem, estoque e vendas antes de agir."
            )
        elif hero_count or anchor_count >= 3:
            headline = f"{category}: arquitetura premium/hero estruturalmente relevante"
            action = (
                "Proteger diferenciação e grade; validar produtividade, margem e "
                "disponibilidade quando dados internos forem conectados."
            )
        else:
            headline = f"{category}: categoria em observação estrutural"
            action = "Monitorar evolução do mix e sinais temporais."

        rows.append({
            "priority": "HIGH" if score >= 75 else "MEDIUM" if score >= 55 else "LOW",
            "scope": "CATEGORY",
            "entity": category,
            "opportunity_score": round(score, 1),
            "evidence_level": _evidence_level(score, evidence_count),
            "headline": headline,
            "recommended_action": action,
            "evidence": (
                f"itens={count}; markdown_watch={markdown_count}; "
                f"hero={hero_count}; premium_anchor={anchor_count}; "
                f"score_medio={avg_score:.1f}"
            ),
        })

    for _, row in clusters.iterrows():
        cluster_id = int(row["portfolio_cluster"])
        score = _clip(max(
            float(row["density_score"]),
            float(row["premium_score"]),
            float(row["markdown_score"]),
        ))

        evidence_count = sum([
            int(row["items"]) >= 10,
            float(row["density_score"]) >= 60,
            float(row["premium_score"]) >= 60,
            float(row["markdown_score"]) >= 60,
        ])

        rows.append({
            "priority": "HIGH" if score >= 75 else "MEDIUM" if score >= 55 else "LOW",
            "scope": "CLUSTER",
            "entity": f"Cluster {cluster_id}",
            "opportunity_score": round(score, 1),
            "evidence_level": _evidence_level(score, evidence_count),
            "headline": (
                f"Cluster {cluster_id}: "
                f"{str(row['cluster_archetype']).replace('_', ' ').title()}"
            ),
            "recommended_action": (
                "Investigar composição e papel do cluster; estes sinais descrevem "
                "estrutura do catálogo, não demanda."
            ),
            "evidence": (
                f"itens={int(row['items'])}; categoria={row['dominant_category']}; "
                f"densidade={row['density_score']}; premium={row['premium_score']}; "
                f"markdown={row['markdown_score']}"
            ),
        })

    selected = products[
        products["product_role"].isin(
            ["HERO_CANDIDATE", "MARKDOWN_WATCH", "PREMIUM_ANCHOR"]
        )
    ].sort_values("product_strategic_score", ascending=False).head(80)

    for _, row in selected.iterrows():
        score = float(row["product_strategic_score"])

        evidence_count = sum([
            score >= 70,
            float(row["size_depth"]) >= 60,
            float(row["price_position"]) >= 70,
            float(row["markdown_pressure"]) >= 80,
        ])

        rows.append({
            "priority": (
                "HIGH"
                if row["product_role"] in ["HERO_CANDIDATE", "MARKDOWN_WATCH"]
                else "MEDIUM"
            ),
            "scope": "PRODUCT",
            "entity": row["name"],
            "opportunity_score": round(score, 1),
            "evidence_level": _evidence_level(score, evidence_count),
            "headline": (
                f"{row['name']}: "
                f"{str(row['product_role']).replace('_', ' ').title()}"
            ),
            "recommended_action": row["recommended_action"],
            "evidence": (
                f"categoria={row['category']}; preço={row['price']}; "
                f"desconto={row['discount_pct']}; grade_score={row['size_depth']:.1f}"
            ),
        })

    out = pd.DataFrame(rows)

    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    evidence_order = {"STRONG": 0, "MODERATE": 1, "EXPLORATORY": 2}

    out["_priority"] = out["priority"].map(priority_order)
    out["_evidence"] = out["evidence_level"].map(evidence_order)

    return (
        out.sort_values(
            ["_priority", "_evidence", "opportunity_score"],
            ascending=[True, True, False],
        )
        .drop(columns=["_priority", "_evidence"])
        .reset_index(drop=True)
    )


def optimization_kpis(catalog: pd.DataFrame) -> dict:
    opportunities = opportunity_engine(catalog)
    similarity = calibrated_similarity(catalog)
    clusters = cluster_intelligence(catalog)

    return {
        "recommendations": int(len(opportunities)),
        "high_priority": int((opportunities["priority"] == "HIGH").sum()),
        "strong_evidence": int(
            (opportunities["evidence_level"] == "STRONG").sum()
        ),
        "calibrated_similarity_pairs": int(len(similarity)),
        "clusters_profiled": int(len(clusters)),
        "sparse_clusters": int(
            (clusters["cluster_archetype"] == "SPARSE_ZONE").sum()
        ),
    }
