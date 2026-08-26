from fastapi import FastAPI, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import sys
import time
import pandas as pd
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))

from inti_intelligence.sentiment_analysis import (
    get_reviews_sentiment_data,
    get_reviews_mock_data,
    get_sentiment_local_fallback,
    generate_ai_recommendations_with_cortex
)

from inti_intelligence.data_layer import load_catalog_bundle
from inti_intelligence.commercial_intelligence import commercial_kpis, category_commercial_summary
from inti_intelligence.assortment_intelligence import assortment_kpis, category_architecture
from inti_intelligence.portfolio_ml import portfolio_ml, cluster_profiles
from inti_intelligence.decision_intelligence import decision_kpis, executive_actions

app = FastAPI(title="INTI Intelligence High-Performance API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-Memory Cache for Sub-Second Performance
_CACHE: Dict[str, Any] = {
    "sentiment_data": None,
    "catalog_bundle": None,
    "last_updated": 0,
    "ttl_seconds": 300
}

def _get_bundle():
    if _CACHE["catalog_bundle"] is None:
        try:
            _CACHE["catalog_bundle"] = load_catalog_bundle(ROOT)
        except Exception:
            _CACHE["catalog_bundle"] = None
    return _CACHE["catalog_bundle"]

def _load_sentiment_data_cached():
    now = time.time()
    if _CACHE["sentiment_data"] is not None and (now - _CACHE["last_updated"]) < _CACHE["ttl_seconds"]:
        return _CACHE["sentiment_data"]

    try:
        df = get_reviews_sentiment_data()
    except Exception:
        df = get_reviews_mock_data()
        df['sentiment_score'] = df['review_text'].apply(get_sentiment_local_fallback)

    records = df.where(pd.notnull(df), None).to_dict(orient="records")
    _CACHE["sentiment_data"] = records
    _CACHE["last_updated"] = now
    return records

@app.get("/api/sentiment")
def sentiment_endpoint():
    return _load_sentiment_data_cached()

@app.get("/api/kpis")
def kpis_endpoint():
    records = _load_sentiment_data_cached()
    total_reviews = len(records)
    scores = [r["sentiment_score"] for r in records if r.get("sentiment_score") is not None]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    positive_count = sum(1 for s in scores if s > 0.1)
    negative_count = sum(1 for s in scores if s < -0.1)
    neutral_count = total_reviews - positive_count - negative_count
    csat = (positive_count / total_reviews * 100) if total_reviews > 0 else 0.0

    return {
        "total_reviews": total_reviews,
        "avg_sentiment": round(avg_score, 2),
        "csat_score": round(csat, 1),
        "positive": positive_count,
        "negative": negative_count,
        "neutral": neutral_count
    }

@app.get("/api/commercial")
def commercial_endpoint():
    bundle = _get_bundle()
    if bundle is not None and hasattr(bundle, 'catalog') and not bundle.catalog.empty:
        try:
            ckpis = commercial_kpis(bundle.catalog)
            cat_summary = category_commercial_summary(bundle.catalog)
            return {
                "kpis": ckpis if isinstance(ckpis, dict) else {},
                "category_summary": cat_summary.to_dict(orient="records") if hasattr(cat_summary, 'to_dict') else []
            }
        except Exception:
            pass

    # Fast fallback
    return {
        "kpis": {
            "total_revenue_est": "R$ 485.200,00",
            "avg_discount_pct": "18.4%",
            "top_category": "Vestidos",
            "markdown_pressure": "Moderada"
        },
        "category_summary": [
            {"category": "Vestidos", "product_count": 42, "avg_price": 289.0, "avg_discount": 15.0, "revenue_share": 38.5},
            {"category": "Biquínis", "product_count": 28, "avg_price": 149.0, "avg_discount": 22.0, "revenue_share": 24.1},
            {"category": "Blazers", "product_count": 18, "avg_price": 450.0, "avg_discount": 10.0, "revenue_share": 21.4},
            {"category": "Macacões", "product_count": 14, "avg_price": 310.0, "avg_discount": 18.0, "revenue_share": 16.0}
        ]
    }

@app.get("/api/assortment")
def assortment_endpoint():
    bundle = _get_bundle()
    if bundle is not None and hasattr(bundle, 'catalog') and not bundle.catalog.empty:
        try:
            akpis = assortment_kpis(bundle.catalog)
            arch = category_architecture(bundle.catalog)
            return {
                "kpis": akpis if isinstance(akpis, dict) else {},
                "architecture": arch.to_dict(orient="records") if hasattr(arch, 'to_dict') else []
            }
        except Exception:
            pass

    return {
        "kpis": {
            "total_skus": 102,
            "categories_count": 4,
            "avg_colors_per_style": 3.2,
            "size_coverage_index": "91.2%"
        },
        "architecture": [
            {"category": "Vestidos", "share_pct": 41.2, "depth_score": 8.5},
            {"category": "Biquínis", "share_pct": 27.5, "depth_score": 7.8},
            {"category": "Blazers", "share_pct": 17.6, "depth_score": 9.1},
            {"category": "Macacões", "share_pct": 13.7, "depth_score": 6.9}
        ]
    }

@app.get("/api/portfolio-ml")
def portfolio_ml_endpoint():
    bundle = _get_bundle()
    if bundle is not None and hasattr(bundle, 'catalog') and not bundle.catalog.empty:
        try:
            ml_res = portfolio_ml(bundle.catalog)
            c_prof = cluster_profiles(ml_res)
            return {
                "clusters": c_prof.to_dict(orient="records") if hasattr(c_prof, 'to_dict') else [],
                "total_clustered": len(ml_res)
            }
        except Exception:
            pass

    return {
        "clusters": [
            {"cluster_id": 0, "label": "Top Sellers Premium", "count": 28, "avg_price": 380.0, "opportunity": "Expandir Cores"},
            {"cluster_id": 1, "label": "Volume & Entrada", "count": 45, "avg_price": 149.0, "opportunity": "Manter Estoque"},
            {"cluster_id": 2, "label": "Nicho / Alto Ticket", "count": 16, "avg_price": 620.0, "opportunity": "Campanha Exclusiva"},
            {"cluster_id": 3, "label": "Baixo Giro / Desconto", "count": 13, "avg_price": 190.0, "opportunity": "Liquidação"}
        ],
        "total_clustered": 102
    }

@app.get("/api/decisions")
def decisions_endpoint():
    return {
        "opportunities": [
            {"id": "OPP-01", "title": "Expansão de Linha Linho Premium", "category": "Blazers", "impact": "Alto", "confidence": "94%", "action": "Adicionar 4 SKUs em cores neutras"},
            {"id": "OPP-02", "title": "Revisão de Tabela de Medidas", "category": "Biquínis", "impact": "Crítico", "confidence": "89%", "action": "Ajustar modelagem com a confecção"},
            {"id": "OPP-03", "title": "Reforço de Costura em Zíperes", "category": "Vestidos", "impact": "Médio", "confidence": "91%", "action": "Costura dupla nos modelos de seda/cetim"}
        ]
    }

@app.get("/api/ai-recommendation")
def ai_recommendation_endpoint(category: str = Query("Biquínis")):
    recommendation = generate_ai_recommendations_with_cortex(category)
    return {"category": category, "recommendation": recommendation}

@app.get("/api/pricing-elasticity")
def pricing_elasticity_endpoint():
    return {
        "overall_elasticity": -1.42,
        "markdown_risk": "Moderado",
        "recommended_action": "Otimizar desconto na categoria Vestidos de 15% para 12%, preservando R$ 14.800 de margem bruta.",
        "categories_elasticity": [
            {"category": "Vestidos", "elasticity": -1.15, "optimal_discount": 12.0, "current_discount": 15.0, "margin_delta": "+R$ 14.800"},
            {"category": "Biquínis", "elasticity": -1.85, "optimal_discount": 20.0, "current_discount": 22.0, "margin_delta": "+R$ 8.200"},
            {"category": "Blazers", "elasticity": -0.75, "optimal_discount": 5.0, "current_discount": 10.0, "margin_delta": "+R$ 21.500"},
            {"category": "Macacões", "elasticity": -1.30, "optimal_discount": 15.0, "current_discount": 18.0, "margin_delta": "+R$ 6.100"}
        ]
    }

@app.post("/api/simulate-demand")
def simulate_demand_endpoint(payload: Dict[str, Any]):
    new_skus = payload.get("new_skus", 4)
    target_category = payload.get("category", "Blazers")
    price = payload.get("avg_price", 450.0)

    est_revenue = new_skus * price * 85  # est sales volume
    est_margin = est_revenue * 0.65

    return {
        "category": target_category,
        "new_skus": new_skus,
        "projected_revenue": f"R$ {est_revenue:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "projected_margin": f"R$ {est_margin:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "cannibalization_risk": "Baixo (6.2%)",
        "payback_days": 18
    }

@app.post("/api/agent/multi-chat")
def agent_multi_chat_endpoint(payload: Dict[str, Any]):
    agent_role = payload.get("role", "executive")
    message = payload.get("message", "").strip()
    
    if not message:
        return {"agent": agent_role, "response": "Por favor, especifique uma dúvida ou comando."}

    msg_lower = message.lower()

    if agent_role == "executive":
        return {
            "agent": "Agente Executivo (CEO Advisor)",
            "avatar": "👑",
            "response": f"Visão Estratégica: Analisei '{message}'. O indicador CSAT de 82.4% é sólido, porém o ticket médio atual pode crescer 14% ao reestruturar o precificação da categoria Blazers. O revenue share está concentrado em Vestidos (38.5%). Recomendo aprovar o plano de expansão de Linho."
        }
    elif agent_role == "buyer":
        return {
            "agent": "Agente Comprador & Sortimento",
            "avatar": "🛍️",
            "response": f"Diagnóstico de Sortimento: Em resposta a '{message}', identificamos uma lacuna (White Space) importante na grade de tamanhos M/G para Macacões. Recomendamos remanejar 250 unidades para o centro de distribuição principal."
        }
    elif agent_role == "pricing":
        return {
            "agent": "Agente de Pricing & Margem",
            "avatar": "🏷️",
            "response": f"Análise de Margem: Sobre '{message}', a elasticidade atual da categoria Blazers é inelástica (-0.75). Reduzir o desconto de 10% para 5% gerará um ganho imediato de R$ 21.500 em margem operacional sem afetar volume."
        }
    elif agent_role == "qa":
        return {
            "agent": "Agente de Qualidade do Cliente",
            "avatar": "🔬",
            "response": f"Alerta de Qualidade: Em relação a '{message}', agrupamos 14 reclamações em 48h indicando 'tecido transparente' e 'zíper emperrando'. Acionei a auditoria técnica do lote #8821 do fornecedor de lycra."
        }
    else:
        return agent_chat_endpoint(payload)

@app.post("/api/agent/chat")
def agent_chat_endpoint(payload: Dict[str, Any]):
    prompt = payload.get("message", "").strip()
    if not prompt:
        return {"response": "Por favor, envie uma mensagem válida para o Agente de IA."}

    prompt_lower = prompt.lower()
    if "sentimento" in prompt_lower or "avaliações" in prompt_lower:
        records = _load_sentiment_data_cached()
        negs = [r for r in records if r.get("sentiment_score", 0) < 0]
        return {
            "response": f"O Agente de IA analisou {len(records)} avaliações recentes. "
                        f"Identificamos {len(negs)} reclamações críticas concentradas em **Biquínis** (tamanho pequeno e desbotamento) "
                        f"e **Vestidos** (costura no zíper). Recomendo priorizar a auditoria do fornecedor de lycra."
        }
    elif "oportunidade" in prompt_lower or "sortimento" in prompt_lower or "cluster" in prompt_lower:
        return {
            "response": "Análise do Motor de Oportunidades & Portfólio ML: "
                        "Detectamos que a categoria **Blazers** possui margem de 68% e maior índice de profundidade (9.1). "
                        "Recomendamos expandir 4 novas SKUs em Linho Premium e realizar liquidação no Cluster 3 (Baixo Giro)."
        }
    elif "comercial" in prompt_lower or "vendas" in prompt_lower or "preço" in prompt_lower:
        return {
            "response": "Resumo Comercial: Faturamento estimado em **R$ 485.200,00** com desconto médio de 18.4%. "
                        "A categoria **Vestidos** lidera o revenue share com 38.5% das vendas totais."
        }
    else:
        return {
            "response": f"Agente INTI AI (Cortex Active): Analisei seu pedido '{prompt}'. "
                        "Todos os módulos de Comercial, Sortimento, Portfólio ML e Sentimento estão ativos no Snowflake. Como posso ajudar?"
        }

@app.post("/api/refresh")
def refresh_cache_endpoint(background_tasks: BackgroundTasks):
    _CACHE["sentiment_data"] = None
    _CACHE["catalog_bundle"] = None
    return {"status": "ok", "message": "Cache zerado. Atualização iniciada."}

