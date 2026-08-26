from __future__ import annotations
import os
import pandas as pd
from inti_intelligence.snowflake_db import get_snowflake_session

# Banco de dados e esquema padrão
DB = "INTI_DB"
SCHEMA = "PUBLIC"

def get_sentiment_local_fallback(text: str) -> float:
    """Calcula um score de sentimento local heurístico se o Cortex não estiver disponível."""
    text_lower = str(text).lower()
    pos_words = ["adorei", "lindo", "maravilhoso", "perfeito", "ótimo", "excelente", "rápido", "recomendo", "bonito", "qualidade", "bom", "confortável"]
    neg_words = ["ruim", "rasgou", "péssimo", "pequeno", "defeito", "desbotou", "atrasou", "sintético", "odiei", "devolvi", "apertado", "frágil"]
    
    score = 0.0
    for w in pos_words:
        if w in text_lower:
            score += 0.25
    for w in neg_words:
        if w in text_lower:
            score -= 0.25
            
    # Garantir limites [-1.0, 1.0]
    return max(-1.0, min(1.0, score))

def get_reviews_mock_data() -> pd.DataFrame:
    """Retorna dados simulados de avaliações de clientes em português."""
    return pd.DataFrame([
        # Vestidos
        {"product_id": "v-1", "category": "Vestidos", "product_name": "Vestido Midi Seda", "review_text": "Adorei o vestido, tecido maravilhoso e caimento impecável! Com certeza comprarei mais."},
        {"product_id": "v-2", "category": "Vestidos", "product_name": "Vestido Longo Floral", "review_text": "A costura do vestido rasgou no primeiro uso perto do zíper. Tecido muito frágil para o preço."},
        {"product_id": "v-3", "category": "Vestidos", "product_name": "Vestido Festa Cetim", "review_text": "Lindo, mas o tamanho ficou um pouco apertado na cintura. A qualidade é excelente."},
        # Biquínis
        {"product_id": "b-1", "category": "Biquínis", "product_name": "Biquíni Cortininha Classic", "review_text": "O biquíni veio muito pequeno e a cor desbotou logo na primeira lavagem. Fiquei decepcionada."},
        {"product_id": "b-2", "category": "Biquínis", "product_name": "Biquíni Asa Delta", "review_text": "Produto de baixa qualidade, o elástico ficou frouxo muito rápido. Não recomendo."},
        # Blazers
        {"product_id": "bl-1", "category": "Blazers", "product_name": "Blazer Linho Premium", "review_text": "Blazer de alfaiataria com excelente caimento. Peça clássica que vale cada centavo."},
        {"product_id": "bl-2", "category": "Blazers", "product_name": "Blazer Estruturado Luxo", "review_text": "Acabamento de luxo incrível. Fiquei muito satisfeita com a qualidade dos botões e forro."},
        # Macacões
        {"product_id": "m-1", "category": "Macacões", "product_name": "Macacão Pantalona Crepe", "review_text": "O caimento é perfeito, mas achei o tecido um pouco sintético e quente para o verão."},
        {"product_id": "m-2", "category": "Macacões", "product_name": "Macacão Utilitário Algodão", "review_text": "Muito confortável e prático. A entrega atrasou dois dias, mas o produto compensa."},
        # Conjuntos
        {"product_id": "c-1", "category": "Conjuntos", "product_name": "Conjunto Tricot Verão", "review_text": "O conjunto encolheu muito na primeira lavagem manual. Devolvi o produto."},
        {"product_id": "c-2", "category": "Conjuntos", "product_name": "Conjunto Alfaiataria Colete", "review_text": "Maravilhoso! Modelagem elegante e tecido muito confortável. Perfeito para trabalhar."}
    ])

def setup_reviews_database(session=None):
    """Cria a tabela de avaliações e popula com os dados simulados se necessário."""
    try:
        if session is None:
            session = get_snowflake_session()
            
        # Cria a tabela de reviews se ela não existir
        session.sql(f"""
        CREATE TABLE IF NOT EXISTS {DB}.{SCHEMA}.PRODUCT_REVIEWS (
            product_id VARCHAR,
            category VARCHAR,
            product_name VARCHAR,
            review_text VARCHAR,
            sentiment_score FLOAT
        );
        """).collect()
        
        # Verifica se já está populada
        count = session.sql(f"SELECT COUNT(*) FROM {DB}.{SCHEMA}.PRODUCT_REVIEWS;").collect()[0][0]
        if count == 0:
            df = get_reviews_mock_data()
            df['sentiment_score'] = 0.0 # Inicializa vazio para ser processado pelo Cortex
            session.create_dataframe(df).write.mode("append").save_as_table(f"{DB}.{SCHEMA}.PRODUCT_REVIEWS")
            print("Tabela PRODUCT_REVIEWS criada e populada com dados simulados!")
        else:
            print(f"Tabela PRODUCT_REVIEWS já existe com {count} registros.")
    except Exception as e:
        print(f"Aviso: Erro ao configurar tabela de reviews no Snowflake ({e}). Usando modo offline.")

def analyze_sentiment_with_cortex(session=None) -> bool:
    """Executa a função nativa SNOWFLAKE.CORTEX.SENTIMENT nos reviews sem score."""
    try:
        if session is None:
            session = get_snowflake_session()
            
        setup_reviews_database(session)
        
        # Atualiza a tabela chamando a IA nativa do Snowflake Cortex
        session.sql(f"""
        UPDATE {DB}.{SCHEMA}.PRODUCT_REVIEWS
        SET sentiment_score = SNOWFLAKE.CORTEX.SENTIMENT(review_text)
        WHERE sentiment_score = 0.0 OR sentiment_score IS NULL;
        """).collect()
        
        print("[OK] Sentimentos atualizados usando Snowflake Cortex AI!")
        return True
    except Exception as e:
        print(f"Aviso: Não foi possível rodar Cortex Sentiment ({e}). Atualizando scores localmente.")
        # Fallback local
        try:
            if session is None:
                return False
            # Carrega reviews locais e calcula heurística
            df = session.table(f"{DB}.{SCHEMA}.PRODUCT_REVIEWS").to_pandas()
            df.columns = [c.lower() for c in df.columns]
            for idx, row in df.iterrows():
                if row['sentiment_score'] == 0.0 or pd.isna(row['sentiment_score']):
                    score = get_sentiment_local_fallback(row['review_text'])
                    session.sql(f"""
                    UPDATE {DB}.{SCHEMA}.PRODUCT_REVIEWS
                    SET sentiment_score = {score}
                    WHERE review_text = '{row['review_text'].replace("'", "''")}';
                    """).collect()
            print("[OK] Sentimentos atualizados localmente (fallback).")
            return True
        except Exception as local_err:
            print(f"Erro no fallback local de sentimento: {local_err}")
            return False

def get_reviews_sentiment_data(session=None) -> pd.DataFrame:
    """Retorna os dados da tabela de avaliações processados."""
    try:
        if session is None:
            session = get_snowflake_session()
            
        analyze_sentiment_with_cortex(session)
        return session.table(f"{DB}.{SCHEMA}.PRODUCT_REVIEWS").to_pandas()
    except Exception as e:
        print(f"Aviso: Falha ao carregar reviews do Snowflake ({e}). Usando mock local.")
        # Retorna mock local pré-calculado
        df = get_reviews_mock_data()
        df['sentiment_score'] = df['review_text'].apply(get_sentiment_local_fallback)
        return df

def generate_ai_recommendations_with_cortex(category: str, session=None) -> str:
    """Gera recomendações de varejo inteligentes usando SNOWFLAKE.CORTEX.COMPLETE."""
    try:
        if session is None:
            session = get_snowflake_session()
            
        # Busca avaliações negativas desta categoria
        df_reviews = session.table(f"{DB}.{SCHEMA}.PRODUCT_REVIEWS").filter(
            f"category = '{category}' AND sentiment_score < 0.0"
        ).to_pandas()
        
        if df_reviews.empty:
            return f"A IA do Snowflake Cortex analisou o catálogo e não encontrou reclamações críticas ou sentimentos negativos pendentes para a categoria **{category}**."
            
        reviews_list = "\\n- ".join(df_reviews['review_text'].tolist())
        
        # Constrói prompt para o Cortex Llama3
        prompt = f"""
        Você é um consultor especialista em varejo de moda de luxo e Inteligência Artificial.
        Com base nas seguintes reclamações reais de clientes sobre a categoria '{category}':
        - {reviews_list}
        
        Forneça uma análise concisa e 3 ações práticas de negócios para corrigir esses problemas de produto ou atendimento e melhorar a retenção de clientes. responda em português, de forma direta e profissional voltada a negócios.
        """
        
        # Escapar aspas simples para SQL
        prompt_escaped = prompt.replace("'", "''")
        
        # Executa o LLM no Snowflake Cortex
        query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3-70b', '{prompt_escaped}') as RESPONSE;"
        result = session.sql(query).collect()
        
        if result and len(result) > 0:
            return result[0]['RESPONSE']
        return "Não foi possível obter resposta da IA do Snowflake."
    except Exception as e:
        print(f"Aviso: Falha no Cortex Complete ({e}). Usando gerador heurístico local.")
        # Fallback local heurístico
        if category == "Biquínis":
            return """**Análise de Sentimento (IA Local Fallback):**
Clientes reclamam que o tamanho veio menor que o padrão e que as cores desbotaram na primeira lavagem.

**Ações Recomendadas:**
1. **Revisão da Ficha Técnica:** Auditar a modelagem e a tabela de medidas de biquínis com a confecção.
2. **Controle de Qualidade de Tecidos:** Solicitar testes de solidez de cor e durabilidade do elastano junto ao fornecedor de lycra.
3. **Comunicação Ativa:** Orientar no site para comprar um tamanho acima se preferir caimento mais confortável."""
        elif category == "Vestidos":
            return """**Análise de Sentimento (IA Local Fallback):**
Há relatos de costura frágil próximo ao zíper e tecidos delicados que rasgaram no primeiro uso.

**Ações Recomendadas:**
1. **Reforço de Costura:** Inserir costura dupla/reforço nas áreas de maior tensão (zíper e costuras laterais) em tecidos finos.
2. **Ajuste de Margem de Costura:** Aumentar a margem interna dos tecidos para evitar desfiamento.
3. **Treinamento de Equipe:** Orientar equipe de vendas a instruir clientes sobre a forma correta de vestir peças delicadas de seda/cetim."""
        else:
            return f"**Análise de Sentimento (IA Local Fallback):**\\nAvaliações monitoradas para a categoria {category} indicam pontos de atenção sobre qualidade de acabamento ou caimento.\\n\\n**Ações Recomendadas:**\\n1. Auditar amostras físicas do lote atual.\\n2. Monitorar feedback pós-venda dos próximos 30 dias.\\n3. Oferecer suporte de troca rápida para clientes insatisfeitos."
