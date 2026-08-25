import pandas as pd
from inti_intelligence.opportunity_engine import (
    calibrated_similarity,
    cluster_intelligence,
    opportunity_engine,
    optimization_kpis,
)


def sample():
    rows = []
    for i in range(10):
        rows.append({
            "name": f"Vestido {i}",
            "category": "Vestidos",
            "color": "Preto" if i < 5 else "Off White",
            "sizes": "36|38|40|42",
            "price": 1500 + i * 30,
            "original_price": 1500 + i * 30,
            "discount_pct": 0,
        })
    for i in range(10):
        rows.append({
            "name": f"Biquíni {i}",
            "category": "Biquínis",
            "color": "Azul",
            "sizes": "P|M|G",
            "price": 120 + i * 4,
            "original_price": 350,
            "discount_pct": 65,
        })
    return pd.DataFrame(rows)


def test_cluster_intelligence():
    result = cluster_intelligence(sample())
    assert len(result) >= 2
    assert {
        "cluster_archetype",
        "density_score",
        "premium_score",
        "markdown_score",
    }.issubset(result.columns)


def test_opportunity_engine():
    result = opportunity_engine(sample())
    assert len(result) > 0
    assert {
        "scope",
        "evidence_level",
        "recommended_action",
        "evidence",
    }.issubset(result.columns)


def test_kpis():
    result = optimization_kpis(sample())
    assert result["recommendations"] > 0


def test_calibrated_similarity_returns_dataframe():
    result = calibrated_similarity(sample(), 70)
    assert isinstance(result, pd.DataFrame)
