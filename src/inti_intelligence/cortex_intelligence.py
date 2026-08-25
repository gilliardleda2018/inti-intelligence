from __future__ import annotations
import pandas as pd
from .snowflake_db import get_snowflake_session

def get_cortex_executive_summary(catalog_df: pd.DataFrame, high_priority_count: int, cluster_count: int) -> str:
    """Generate an executive summary using Snowflake Cortex AI LLM."""
    if catalog_df.empty:
        return "Nenhum dado disponível no catálogo para análise no momento."

    # Top categories in catalog
    top_cats = catalog_df['category'].value_counts().head(3).index.tolist()
    top_cats_str = ", ".join(top_cats) if top_cats else "Nenhuma"

    # Average discount
    avg_discount = 0.0
    if 'discount_pct' in catalog_df.columns:
        avg_discount = float(catalog_df['discount_pct'].mean() * 100)

    prompt = f"""
    Você é o INTI Intelligence AI, assistente executivo estratégico para análise de mix de produtos.
    Escreva um resumo executivo corporativo sucinto (máximo 4 linhas) em português com base nos seguintes indicadores do catálogo:
    - Total de produtos no catálogo: {len(catalog_df)}
    - Alertas de alta prioridade gerados: {high_priority_count}
    - Principais categorias analisadas: {top_cats_str}
    - Desconto médio observado: {avg_discount:.1f}%
    - Grupos estruturais identificados pelo ML: {cluster_count}

    Foque em oportunidades de otimização de sortimento de forma profissional e sofisticada.
    """
    
    # Escape single quotes in prompt to prevent SQL injection in statement
    prompt_safe = prompt.replace("'", "''")

    try:
        session = get_snowflake_session()
        # Query Cortex AI using llama3-8b for optimal speed and cost-efficiency
        query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3-8b', '{prompt_safe}') as response"
        result = session.sql(query).collect()
        if result and len(result) > 0:
            summary = result[0]['RESPONSE']
            return summary.strip()
    except Exception as e:
        # Fallback to local heuristic description if Cortex is offline/unauthorized
        print(f"Alerta: Snowflake Cortex AI indisponível ({e}). Usando resumo heurístico local.")
        
    return (
        f"Análise concluída para {len(catalog_df)} variantes em {cluster_count} grupos de estilo. "
        f"Foram identificados {high_priority_count} sinais de alta prioridade. "
        f"O desconto médio do portfólio está em {avg_discount:.1f}%, concentrado nas categorias {top_cats_str}."
    )
