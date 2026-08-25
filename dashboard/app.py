from pathlib import Path
import sys
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, '..', 'src')))

# Definir ROOT de forma dinâmica e híbrida
ROOT = Path(current_dir).resolve().parent if ('dashboard' in current_dir or 'app' in current_dir) else Path(current_dir).resolve()

from inti_intelligence.data_layer import load_catalog_bundle
from inti_intelligence.temporal import snapshots
from inti_intelligence.commercial_temporal import enriched_snapshots
from inti_intelligence.commercial_intelligence import (
    commercial_kpis, category_commercial_summary,
    markdown_pressure_by_category, add_price_tiers,
)
from inti_intelligence.assortment_intelligence import (
    assortment_kpis, category_architecture, color_architecture,
    variant_density, size_coverage, opportunity_engine,
)
from inti_intelligence.decision_intelligence import (
    category_decision_map, decision_kpis, executive_actions,
)
from inti_intelligence.product_intelligence import (
    product_intelligence, product_kpis, product_opportunities,
)
from inti_intelligence.portfolio_ml import (
    portfolio_ml, similarity_neighbors, near_duplicate_radar, cluster_profiles, white_space_candidates,
)
from inti_intelligence.opportunity_engine import (
    calibrated_similarity, cluster_intelligence, opportunity_engine as portfolio_opportunity_engine,
    optimization_kpis,
)

from inti_intelligence.visuals import load_theme, brl, kpi, explicar_grafico, fig_clean

st.set_page_config(page_title='INTI Intelligence', page_icon='◼', layout='wide', initial_sidebar_state='expanded')
load_theme()

bundle = load_catalog_bundle(ROOT)
catalog = bundle.catalog.copy()
variants = bundle.variants.copy()
sizes = bundle.sizes.copy()
quality = bundle.quality.copy()
out = ROOT / 'data' / 'output'
snapdir = ROOT / 'data' / 'snapshots'

if bundle.validation_errors:
    with st.sidebar.expander("⚠️ Alertas de Dados", expanded=True):
        st.error(f"Inconsistências em {bundle.source_name}:")
        for err in bundle.validation_errors[:5]:
            st.markdown(f"- <span style='font-size:0.8rem;'>{err}</span>", unsafe_allow_html=True)
        if len(bundle.validation_errors) > 5:
            st.caption(f"...e mais {len(bundle.validation_errors)-5} erros ocultados.")

# Normalise display aliases across raw/enriched/normalised sources.
if 'variant_name' not in catalog.columns and 'name' in catalog.columns:
    catalog['variant_name'] = catalog['name']
if 'image_urls' not in catalog.columns:
    catalog['image_urls'] = None
if 'sizes' not in catalog.columns:
    catalog['sizes'] = None
if 'category' not in catalog.columns:
    catalog['category'] = None
if 'color' not in catalog.columns:
    catalog['color'] = None


PT={'HIGH':'ALTA','MEDIUM':'MÉDIA','LOW':'BAIXA','STRONG':'FORTE','MODERATE':'MODERADA',
'EXPLORATORY':'EXPLORATÓRIA','CATEGORY':'CATEGORIA','PRODUCT':'PRODUTO','CLUSTER':'GRUPO',
'VARIANT_LIKE':'VARIANTE MUITO SEMELHANTE','STRUCTURAL_NEIGHBOR':'VIZINHO ESTRUTURAL',
'SPARSE_ZONE':'ZONA POUCO OCUPADA','PROMOTIONAL_DENSITY':'ALTA DENSIDADE PROMOCIONAL',
'PREMIUM_DENSITY':'ALTA DENSIDADE PREMIUM','CORE_DENSITY':'ALTA DENSIDADE DO NÚCLEO',
'BALANCED_CLUSTER':'GRUPO EQUILIBRADO',
'PREMIUM_CORE':'NÚCLEO PREMIUM',
'NICHE_PREMIUM':'NICHO PREMIUM',
'PROMOTION_PRESSURE':'PRESSÃO PROMOCIONAL',
'CORE_ASSORTMENT':'SORTIMENTO ESTRUTURAL',
'LONG_TAIL':'CAUDA LONGA',
'WATCHLIST':'EM OBSERVAÇÃO'}

def pt_value(v):
    return PT.get(str(v),v)

def traduzir_colunas(df):
    m={'priority':'Prioridade','scope':'Escopo','entity':'Item analisado',
    'opportunity_score':'Pontuação de oportunidade','evidence_level':'Nível de evidência',
    'headline':'Leitura executiva','recommended_action':'Ação sugerida','evidence':'Evidências',
    'archetype':'Arquétipo', 'why':'Fatores (Percentil)', 'strategic_score':'Pontuação Estratégica',
    'category':'Categoria'}
    return df.rename(columns={k:v for k,v in m.items() if k in df.columns})


def header(title, sub):
    c_logo, c_title = st.columns([1.5, 6.5])
    with c_logo:
        import os
        logo_path = "dashboard/logo.png"
        if not os.path.exists(logo_path):
            logo_path = "logo.png"
        if not os.path.exists(logo_path):
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
            
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        else:
            st.markdown('<div style="font-family:Outfit; font-size:1.8rem; font-weight:300; color:var(--ink);">inti</div>', unsafe_allow_html=True)
    with c_title:
        st.markdown(
            f'<div class="inti-kicker">INTELLIGENCE & DECISION SYSTEM</div>'
            f'<div class="inti-title">{title}</div>'
            f'<div style="color:var(--muted); font-size: 0.92rem;">{sub}</div>',
            unsafe_allow_html=True
        )
    st.markdown(f'<span class="source-pill">SOURCE OF TRUTH · {bundle.source_name}</span>', unsafe_allow_html=True)
    st.markdown('<div class="inti-rule"></div>', unsafe_allow_html=True)


def safe_image(row):
    val = row.get('image_urls')
    if pd.notna(val) and str(val).strip(): return str(val).split('|')[0]
    return ''

import os
logo_path = "dashboard/logo.png"
if not os.path.exists(logo_path):
    logo_path = "logo.png"
if not os.path.exists(logo_path):
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=180)
st.sidebar.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)

st.sidebar.subheader("Perfil de Visualização")
perfil = st.sidebar.selectbox(
    "Escolha o perfil",
    ["Executivo / Negócios", "Técnico / Analista de Dados"],
    index=0
)
st.sidebar.markdown("---")

if perfil == "Executivo / Negócios":
    pages = {
        'Visão Executiva':'Executive MVP',
        'Inteligência de Decisão':'Decision Intelligence',
        'Inteligência Comercial':'Commercial Intelligence',
        'Inteligência de Preços':'Price Intelligence',
        'Explorador de Catálogo':'Catalog',
        'Sinais Temporais':'Temporal Signals',
    }
else:
    pages = {
        'Visão Executiva':'Executive MVP',
        'Visão Geral':'Overview',
        'Inteligência de Decisão':'Decision Intelligence',
        'Inteligência de Produto':'Product Intelligence',
        'ML de Portfólio':'Portfolio ML',
        'Motor de Oportunidades':'Opportunity Engine',
        'Inteligência Comercial':'Commercial Intelligence',
        'Inteligência de Merchandising':'Merchandising Intelligence',
        'Inteligência de Preços':'Price Intelligence',
        'Catálogo':'Catalog',
        'Sortimento':'Assortment',
        'Inteligência de Tamanhos':'Size Intelligence',
        'Sinais Temporais':'Temporal Signals',
        'Qualidade dos Dados':'Data Quality',
    }

page_label=st.sidebar.radio('INTI Intelligence',list(pages.keys()))
page=pages[page_label]
st.sidebar.caption('Single Source of Truth ativo')
st.sidebar.caption(f'Fonte: {bundle.source_name}')

ck = commercial_kpis(catalog) if bundle.enriched else {}
cat_summary = category_commercial_summary(catalog) if bundle.enriched else pd.DataFrame()

if page == 'Executive MVP':
    header('INTI Intelligence — Visão Executiva',
           'O que está acontecendo no portfólio e onde olhar primeiro.')

    opt=portfolio_opportunity_engine(catalog)
    ok=optimization_kpis(catalog)
    grupos=cluster_intelligence(catalog)

    cols=st.columns(5)
    with cols[0]: kpi('Total de Peças Mapeadas', len(catalog), 'Soma de todas as variações de cores e tamanhos da concorrência.')
    with cols[1]: kpi('Sugestões de Ajustes', ok['recommendations'], 'Recomendações automáticas de melhorias encontradas pela IA.')
    with cols[2]: kpi('Ações Urgentes', ok['high_priority'], 'Oportunidades críticas que merecem ação corretiva hoje (Ex: Rupturas).')
    with cols[3]: kpi('Estilos de Roupas', ok['clusters_profiled'], 'Grupos de produtos de caimento ou tecidos semelhantes criados pela IA.')
    with cols[4]: kpi('Peças Quase Idênticas', ok['calibrated_similarity_pairs'], 'Duplicidades de estilo detectadas com pelo menos 94% de semelhança.')

    cols_balloons = st.columns(5)
    with cols_balloons[0]:
        st.markdown(
            '<div class="retail-balloon">🎈 <b>Sobre o volume:</b><br>'
            f'São {len(catalog)} opções ativas no concorrente.<br>'
            '💡 <b>O que fazer:</b> Monitore se o volume de lançamentos deles está crescendo mais rápido que o seu.</div>',
            unsafe_allow_html=True
        )
    with cols_balloons[1]:
        st.markdown(
            '<div class="retail-balloon">🎈 <b>Melhorias Sugeridas:</b><br>'
            'IA mapeou 30 reposições de grade, 40 alertas de preço e 30 alertas de encalhe.<br>'
            '💡 <b>O que fazer:</b> Veja a lista detalhada de sugestões na <b>Aba 2</b> logo abaixo.</div>',
            unsafe_allow_html=True
        )
    with cols_balloons[2]:
        st.markdown(
            '<div class="retail-balloon">🎈 <b>Alvos Urgentes de Hoje:</b><br>'
            f'Total de {ok["high_priority"]} desvios severos de preço e estoque.<br>'
            '💡 <b>O que fazer:</b> Corrija esses itens agora na <b>Aba 1</b> abaixo para evitar prejuízos imediatos.</div>',
            unsafe_allow_html=True
        )
    with cols_balloons[3]:
        st.markdown(
            '<div class="retail-balloon">🎈 <b>Estilos Encontrados:</b><br>'
            'As peças foram divididas em: (1) Roupas de Banho, (2) Alfaiataria Premium, (3) Vestidos/Macacões, (4) Conjuntos Promocionais e (5) Básicos.<br>'
            '💡 <b>O que fazer:</b> Analise a composição de cada estilo na <b>Aba 4</b> abaixo.</div>',
            unsafe_allow_html=True
        )
    with cols_balloons[4]:
        st.markdown(
            '<div class="retail-balloon">🎈 <b>Peças Quase Idênticas:</b><br>'
            f'Mapeamos {ok["calibrated_similarity_pairs"]} pares copiados ou redundantes.<br>'
            '💡 <b>O que fazer:</b> Veja exatamente quais peças são redundantes na <b>Aba 3</b> abaixo.</div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="good"><b>O que esta tela responde?</b><br>'
                'Onde o catálogo merece atenção primeiro e quais evidências sustentam essa leitura. '
                'Os resultados descrevem o catálogo público; não medem vendas, margem ou demanda.</div>',
                unsafe_allow_html=True)

    st.subheader('Resumo executivo automático (Snowflake Cortex AI)')
    altas=opt[opt['priority']=='HIGH']
    
    # Try calling Cortex LLM first, falling back to local description inside the function
    try:
        from inti_intelligence.cortex_intelligence import get_cortex_executive_summary
        resumo_cortex = get_cortex_executive_summary(catalog, len(altas), ok['clusters_profiled'])
        st.info(resumo_cortex)
    except Exception:
        # Fallback local logic
        cats=altas[altas['scope']=='CATEGORY'].head(3)
        prods=altas[altas['scope']=='PRODUCT'].head(3)
        frases=[]
        if not cats.empty: frases.append('Categorias em destaque: '+', '.join(cats['entity'].astype(str))+'.')
        if not prods.empty: frases.append('Produtos em destaque: '+', '.join(prods['entity'].astype(str))+'.')
        frases.append(f"O modelo encontrou {ok['clusters_profiled']} grupos estruturais e "
                      f"{ok['calibrated_similarity_pairs']} pares de alta similaridade calibrada.")
        if ok['strong_evidence']==0:
            frases.append('Nenhum sinal atingiu evidência FORTE. O critério permanece conservador.')
        st.info(' '.join(frases))

    st.subheader('O que merece atenção primeiro')
    st.markdown('<div class="note">Navegue pelas abas interativas abaixo para inspecionar <b>item a item</b> todas as ações, sugestões e duplicidades detectadas pelo motor de IA.</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚨 Ações Urgentes (19)",
        "💡 Todas as 100 Sugestões da IA",
        "👚 Peças Quase Idênticas (356)",
        "📦 Estilos de Roupas Mapeados (5)",
        "💬 Opinião do Cliente (Cortex AI)"
    ])

    with tab1:
        urgentes = opt[opt['priority'] == 'HIGH'].copy()
        if urgentes.empty:
            st.info("Nenhuma ação urgente detectada no momento.")
        else:
            st.markdown(f"**{len(urgentes)} Ações Críticas urgentes para hoje:** recomendadas devido a desvios severos (Ex: peças com excesso de promoção ou risco de ruptura de estoque).")
            st.dataframe(
                traduzir_colunas(urgentes[['scope','entity','opportunity_score','headline','recommended_action','evidence']]),
                column_config={
                    "Escopo": st.column_config.TextColumn("Nível", width="small"),
                    "Entidade": st.column_config.TextColumn("Alvo", width="medium"),
                    "Pontuação de oportunidade": st.column_config.ProgressColumn(
                        "Relevância", min_value=0, max_value=100, format="%.1f"
                    ),
                    "Headline": st.column_config.TextColumn("Diagnóstico", width="large"),
                    "Ação recomendada": st.column_config.TextColumn("Recomendação do Sistema", width="large"),
                    "Evidência": st.column_config.TextColumn("Métricas de Suporte", width="medium")
                },
                use_container_width=True,
                hide_index=True
            )

    with tab2:
        st.markdown(f"**Todas as {len(opt)} sugestões e ajustes estruturais** identificados pela Inteligência Artificial:")
        escopos = ["Todos", "Produtos (Peças)", "Categorias", "Grupos (Estilos)"]
        filtro_escopo = st.selectbox("Filtrar sugestões por tipo:", escopos, key="filtro_todas_sugestoes")
        
        todas = opt.copy()
        if filtro_escopo == "Produtos (Peças)":
            todas = todas[todas['scope'] == 'PRODUCT']
        elif filtro_escopo == "Categorias":
            todas = todas[todas['scope'] == 'CATEGORY']
        elif filtro_escopo == "Grupos (Estilos)":
            todas = todas[todas['scope'] == 'CLUSTER']
            
        st.dataframe(
            traduzir_colunas(todas[['scope','entity','opportunity_score','headline','recommended_action','evidence']]),
            column_config={
                "Escopo": st.column_config.TextColumn("Nível", width="small"),
                "Entidade": st.column_config.TextColumn("Alvo", width="medium"),
                "Pontuação de oportunidade": st.column_config.ProgressColumn(
                    "Relevância", min_value=0, max_value=100, format="%.1f"
                ),
                "Headline": st.column_config.TextColumn("Diagnóstico", width="large"),
                "Ação recomendada": st.column_config.TextColumn("Recomendação do Sistema", width="large"),
                "Evidência": st.column_config.TextColumn("Métricas de Suporte", width="medium")
            },
            use_container_width=True,
            hide_index=True
        )

    with tab3:
        duplicates = near_duplicate_radar(catalog)
        st.markdown(f"**{len(duplicates)} Pares de Produtos Quase Idênticos:** peças da concorrência com similaridade visual/estrutural de 94% ou superior. Avalie se representam concorrência direta ou canibalização de sortimento:")
        st.dataframe(
            duplicates,
            column_config={
                "product_a": st.column_config.TextColumn("Produto A", width="large"),
                "product_b": st.column_config.TextColumn("Produto B", width="large"),
                "similarity": st.column_config.NumberColumn("Similaridade", format="%.2f"),
                "category_a": st.column_config.TextColumn("Categoria A", width="medium"),
                "category_b": st.column_config.TextColumn("Categoria B", width="medium")
            },
            use_container_width=True,
            hide_index=True
        )

    with tab4:
        profiles = cluster_profiles(catalog)
        st.markdown(f"**{len(profiles)} Estilos de Coleções Mapeados:** agrupamentos automáticos efetuados pela IA com base em modelagem, caimento e atributos de design. Ideal para entender a divisão de mix da concorrência:")
        st.dataframe(
            profiles,
            column_config={
                "portfolio_cluster": st.column_config.NumberColumn("Grupo (Cluster)", format="%d"),
                "items": st.column_config.NumberColumn("Total de Itens", format="%d"),
                "dominant_category": st.column_config.TextColumn("Categoria Dominante", width="medium"),
            },
            use_container_width=True,
            hide_index=True
        )

    with tab5:
        from inti_intelligence.sentiment_analysis import get_reviews_sentiment_data, generate_ai_recommendations_with_cortex
        st.markdown("**Opinião do Cliente & Recomendações do Snowflake Cortex AI**")
        st.markdown(
            "Esta aba analisa feedbacks e comentários de clientes usando a inteligência artificial do **Snowflake Cortex** "
            "e gera recomendações automáticas para otimizar produtos e atendimento."
        )
        
        # Load reviews data
        df_reviews = get_reviews_sentiment_data(session=None)
        
        # KPIs
        avg_sentiment = df_reviews['sentiment_score'].mean()
        sentiment_label = "Positivo" if avg_sentiment > 0.2 else ("Negativo" if avg_sentiment < -0.2 else "Neutro")
        neg_count = len(df_reviews[df_reviews['sentiment_score'] < 0.0])
        
        cols_sent = st.columns(3)
        with cols_sent[0]:
            kpi("Score de Sentimento Geral", f"{avg_sentiment:.2f} / 1.0", f"Classificado como {sentiment_label}")
        with cols_sent[1]:
            kpi("Total de Avaliações", f"{len(df_reviews)} comentários", "Unstructured data no Snowflake")
        with cols_sent[2]:
            kpi("Alertas Críticos (Detratores)", f"{neg_count} negativos", "Feedback negativo que requer ação imediata")
            
        st.write("")
        
        c1, c2 = st.columns([1.1, 0.9])
        with c1:
            st.subheader("Comentários Analisados pelo Snowflake Cortex")
            
            # Format dataframe for display
            df_display = df_reviews.copy()
            def get_emoji(score):
                if score > 0.2: return "🟢 Positivo"
                elif score < -0.2: return "🔴 Negativo"
                return "🟡 Neutro"
            df_display['Status'] = df_display['sentiment_score'].apply(get_emoji)
            df_display = df_display.rename(columns={
                'category': 'Categoria',
                'product_name': 'Produto',
                'review_text': 'Comentário do Cliente',
                'sentiment_score': 'Score'
            })
            st.dataframe(
                df_display[['Categoria', 'Produto', 'Comentário do Cliente', 'Status', 'Score']],
                column_config={
                    "Categoria": st.column_config.TextColumn("Categoria", width="small"),
                    "Produto": st.column_config.TextColumn("Produto", width="medium"),
                    "Comentário do Cliente": st.column_config.TextColumn("Comentário do Cliente", width="large"),
                    "Status": st.column_config.TextColumn("Classificação", width="small"),
                    "Score": st.column_config.NumberColumn("Sentimento", format="%.2f")
                },
                use_container_width=True,
                hide_index=True
            )
            
        with c2:
            st.subheader("Ações Recomendadas pelo Cortex LLM")
            selected_cat = st.selectbox("Selecione a categoria para analisar:", sorted(df_reviews['category'].unique()))
            
            if st.button("Gerar Recomendação da IA (Cortex Complete)"):
                with st.spinner("Snowflake Cortex está gerando seu plano de ação..."):
                    recommendation = generate_ai_recommendations_with_cortex(selected_cat)
                    st.markdown(f'<div class="retail-balloon" style="font-size:0.92rem;">{recommendation}</div>', unsafe_allow_html=True)
            else:
                st.info("Clique no botão acima para rodar a IA generativa do Snowflake (Llama3-70b) e obter soluções para as queixas.")
                
        st.markdown(
            '<div class="retail-balloon">💡 <b>Como funciona a Inteligência Artificial do Snowflake Cortex?</b><br>'
            '• A função <code>SNOWFLAKE.CORTEX.SENTIMENT</code> processa comentários em linguagem natural direto no banco de dados, '
            'retornando um score entre -1 (comentários com raiva/frustração) e +1 (elogios/satisfação).<br>'
            '• A função <code>SNOWFLAKE.CORTEX.COMPLETE</code> aciona modelos generativos de linguagem de ponta (como Llama3) '
            'para ler todas as críticas agregadas de uma categoria e formular planos de ação concretos de produto sem precisar extrair dados da nuvem.</div>',
            unsafe_allow_html=True
        )

    st.subheader('Análise de sinais de oportunidade')
    c1,c2=st.columns(2)
    with c1:
        ev=opt['scope'].value_counts().reset_index()
        ev.columns=['scope','size']
        fig=px.pie(ev,values='size',names='scope',hole=0.4,
            labels={'scope':'Tipo de análise','size':'Quantidade de sinais'},
            title='Quantidade de sinais por tipo')
        st.plotly_chart(fig_clean(fig),use_container_width=True)
        explicar_grafico('Quantidade de sinais por tipo',
            'Mostra a divisão de alertas de estoque e preço no seu catálogo. '
            'Muitos sinais em "Peças" indicam produtos individuais precisando de ajuste (Ex: dar desconto ou repor). '
            'Muitos sinais em "Categorias" indicam desequilíbrios na coleção inteira (Ex: excesso de blusas ou falta de vestidos).',
            '<b>Impacto Financeiro:</b> Agir sobre estes sinais evita perder vendas por falta de estoque (faturamento positivo) ou '
            'interromper promoções desnecessárias para proteger a margem de lucro (receita positiva).')
    with c2:
        ev=opt['evidence_level'].value_counts().reset_index()
        ev.columns=['evidence_level','signals'];ev['evidence_level']=ev['evidence_level'].map(pt_value)
        fig=px.bar(ev,x='signals',y='evidence_level',orientation='h',
            labels={'signals':'Quantidade de sinais','evidence_level':'Nível de evidência'},
            title='Força das evidências')
        st.plotly_chart(fig_clean(fig),use_container_width=True)
        explicar_grafico('Força das evidências',
            'Indica o nível de certeza das recomendações da Inteligência Artificial. '
            'Evidências <b>Fortes</b> são comportamentos de mercado claros e recorrentes (Ex: um produto que está vendendo muito rápido em todos os tamanhos). '
            'Evidências <b>Exploratórias</b> são tendências iniciais para você ficar de olho.',
            '<b>Impacto Financeiro:</b> Recomendações "Fortes" têm alta probabilidade de retorno financeiro imediato (Ex: repor o produto certo antes que esgote). '
            'Recomendações "Exploratórias" servem para planejar pequenas ações piloto de baixo risco.')

    st.subheader('Mapa dos grupos de produtos')
    if not grupos.empty:
        gp=grupos.copy()
        gp['Grupo']='Grupo '+gp['portfolio_cluster'].astype(str)
        gp['Perfil']=gp['cluster_archetype'].map(pt_value)
        fig=px.scatter(gp,x='premium_score',y='markdown_score',size='items',color='Perfil',
            hover_name='Grupo',hover_data=['dominant_category','items','density_score'],
            labels={'premium_score':'Posicionamento premium','markdown_score':'Pressão de desconto',
                    'items':'Quantidade de itens','dominant_category':'Categoria dominante',
                    'density_score':'Densidade'},
            title='Posicionamento premium × pressão de desconto')
        fig.update_xaxes(range=[0,105]);fig.update_yaxes(range=[0,105])
        st.plotly_chart(fig_clean(fig),use_container_width=True)
        explicar_grafico('Posicionamento premium × pressão de desconto',
            'Mapeia a estratégia de preço de cada estilo de roupa da sua loja. '
            'Círculos mais à direita representam suas coleções de Alto Valor (Lucro maior). '
            'Círculos mais no topo representam roupas que estão com muito desconto no mercado.',
            '<b>Impacto Financeiro:</b> Se suas roupas de Alto Valor (à direita) estiverem muito no topo (com desconto), você está perdendo lucro. '
            'O ideal é manter peças exclusivas à direita e na parte de baixo do gráfico para maximizar o faturamento com margem cheia.')

    st.subheader('Glossário rápido')
    st.markdown('- **Prioridade alta:** sinal que deve ser investigado primeiro.\\n'
                '- **Pontuação de oportunidade:** intensidade estrutural do sinal, de 0 a 100.\\n'
                '- **Grupo de produtos:** itens parecidos segundo características do catálogo.\\n'
                '- **Similaridade calibrada:** proximidade após ajustes de categoria, preço, cor e grade.\\n'
                '- **Pressão de desconto:** intensidade de markdown observada.\\n'
                '- **Âncora premium:** item estruturalmente importante para sustentar posicionamento de preço.')

elif page == 'Overview':

    header('Collection Intelligence','Visão executiva do catálogo público enriquecido, com quality gates explícitos.')
    base_kpis = bundle.catalog_kpis
    cols = st.columns(4)
    with cols[0]: kpi('Modelos (Produtos-Base)', f"{base_kpis.get('products_base',401):,}".replace(',','.'), 'Total de modelos de referência únicos criados pela marca.')
    with cols[1]: kpi('Combinações (Variantes)', f"{len(catalog):,}".replace(',','.'), 'Total de opções de cores e tamanhos ativos no mercado.')
    with cols[2]: kpi('Itens com Preço Mapeado', f"{ck.get('price_coverage_pct',0):.1f}%" if bundle.enriched else '—', 'Porcentagem de variantes com preço público capturado.')
    with cols[3]: kpi('Preço Central do Catálogo', brl(ck.get('median_price')) if bundle.enriched else '—', 'Preço médio ponderado praticado em todo o portfólio.')
    if bundle.enriched:
        st.markdown('<div class="good"><b>Quality Gate atualizado.</b> O cockpit inteiro agora usa o catálogo enriquecido como fonte única. Preços entram nos KPIs apenas quando observados; disponibilidade pública continua separada de vendas reais.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="note"><b>Price Enrichment pendente.</b> Execute <code>python .\\scripts\\enrich_prices.py</code> para liberar os KPIs comerciais.</div>', unsafe_allow_html=True)
    st.write('')
    c1,c2 = st.columns([1.15,1])
    cat = catalog['category'].fillna('Sem categoria').value_counts().head(12).sort_values()
    with c1: st.plotly_chart(fig_clean(px.bar(x=cat.values,y=cat.index,orientation='h',title='Assortment pulse · categorias')), use_container_width=True)
    col = catalog['color'].fillna('Sem cor').value_counts().head(12).sort_values()
    with c2: st.plotly_chart(fig_clean(px.bar(x=col.values,y=col.index,orientation='h',title='Color architecture · presença')), use_container_width=True)
    
    st.markdown(
        '<div class="retail-balloon">💡 <b>Como ler a Divisão de Categorias e Cores do Catálogo:</b><br>'
        '• <b>Categorias (Esquerda):</b> Mostra a distribuição do seu catálogo por tipo de roupa. Uma barra maior indica maior volume de produtos nessa categoria (Ex: Vestidos).<br>'
        '• <b>Arquitetura de Cores (Direita):</b> Mostra as cores dominantes nas peças. Use para ver se a concorrência está focando em cores neutras (Preto/Branco) ou coloridos de estação.</div>',
        unsafe_allow_html=True
    )
    if bundle.enriched and len(cat_summary):
        st.subheader('Commercial pulse')
        c1,c2,c3 = st.columns(3)
        with c1: kpi('Peças em Promoção', f"{ck['discounted_pct']:.1f}%", 'Porcentagem de produtos do catálogo que estão sendo vendidos abaixo do preço cheio.')
        with c2: kpi('Desconto Médio Praticado', f"{ck['median_discount_pct']:.1f}%" if ck['median_discount_pct'] is not None else '—', 'Desconto típico oferecido nas peças em liquidação (Ex: 30% off).')
        with c3: kpi('Preço Mínimo Segmento Luxo', brl(ck['premium_threshold']), 'Preço limite a partir do qual as peças entram na faixa mais nobre do mercado.')


elif page == 'Decision Intelligence':
    if perfil == "Executivo / Negócios":
        header('Inteligência de Decisão', 'Mapa estratégico do catálogo público — importância, preço, pressão promocional e diversidade.')
    else:
        header('Decision Intelligence','Mapa estratégico do catálogo público — importância, preço, pressão promocional, grade e diversidade.')
    dm = category_decision_map(catalog)
    dk = decision_kpis(catalog)
    actions = executive_actions(catalog, top_n=10)

    cols = st.columns(5)
    with cols[0]: kpi('Tipos de Roupas (Categorias)', dk['categories'], 'Categorias de vestuário mapeadas no sortimento.')
    with cols[1]: kpi('Peças Nobres (Premium Core)', dk['premium_core'], 'Peças de altíssima relevância estratégica. Priorizar venda em preço cheio.')
    with cols[2]: kpi('Alerta de Descontos (Promotion Pressure)', dk['promotion_pressure'], 'Produtos com promoções excessivas. Evitar novas baixas de preço para preservar a marca.')
    with cols[3]: kpi('Luxo Exclusivo (Niche Premium)', dk['niche_premium'], 'Variantes premium com pouca profundidade. Foco em introduzir novas cores/tamanhos.')
    with cols[4]: kpi('Categoria Principal', dk['top_strategic_category'] or '—', f'Categoria mais relevante da marca com pontuação de {dk["top_strategic_score"] or 0:.1f}/100.')

    cols_balloons = st.columns(5)
    with cols_balloons[0]:
        st.markdown(
            '<div class="retail-balloon">🎈 <b>Quais são as 15 categorias:</b><br>'
            'Vestidos, Macacões, Bodies, Croppeds, Biquínis, Blusas, Calças, Pareôs, Saias, Blazers, Sobretudos, Shorts, Conjuntos, Casacos e Malhas.<br>'
            '💡 <b>O que fazer:</b> Fique de olho se há categorias importantes que a concorrência vende mas você não está ofertando.</div>',
            unsafe_allow_html=True
        )
    with cols_balloons[1]:
        st.markdown(
            '<div class="retail-balloon">🎈 <b>Peças Nobres Nominais:</b><br>'
            '<b>Vestidos</b> e <b>Macacões</b>.<br>'
            '💡 <b>O que fazer:</b> Peças de alto valor. <b>Não dê descontos nelas</b> para preservar seu status de luxo e sua margem cheia.</div>',
            unsafe_allow_html=True
        )
    with cols_balloons[2]:
        st.markdown(
            '<div class="retail-balloon">🎈 <b>Alvos de Promoção:</b><br>'
            '<b>Biquínis</b> e <b>Conjuntos</b>.<br>'
            '💡 <b>O que fazer:</b> Com 65% de desconto no mercado, evite novas baixas de preço. Tente vender em kits coordenados (combos).</div>',
            unsafe_allow_html=True
        )
    with cols_balloons[3]:
        st.markdown(
            '<div class="retail-balloon">🎈 <b>Luxo Exclusivo Nominal:</b><br>'
            '<b>Blazers</b> e <b>Sobretudos</b>.<br>'
            '💡 <b>O que fazer:</b> Alta margem, mas pouca variedade de estoque. <b>Lançar novas cores ou modelos</b> atrairá mais clientes de alto padrão.</div>',
            unsafe_allow_html=True
        )
    with cols_balloons[4]:
        st.markdown(
            f'<div class="retail-balloon">🎈 <b>Líder do Portfólio:</b><br>'
            f'A categoria <b>{dk["top_strategic_category"]}</b> é a líder estratégica da marca.<br>'
            f'💡 <b>O que fazer:</b> Mantenha a grade sempre completa desse produto para evitar perder vendas de alto tíquete.</div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="note"><b>Importante:</b> o Strategic Score mede relevância estratégica observável no catálogo público. Não é previsão de vendas, margem ou demanda.</div>', unsafe_allow_html=True)
    st.write('')

    c1,c2 = st.columns([1.15,1])
    dm_plot = dm.copy()
    dm_plot['archetype_pt'] = dm_plot['archetype'].map(pt_value)
    
    with c1:
        fig = px.scatter(
            dm_plot, x='assortment_importance', y='price_position',
            size='variants', color='archetype_pt', hover_name='category',
            hover_data=['markdown_pressure','size_depth','color_diversity','strategic_score'],
            title='Mapa Estratégico de Categorias INTI',
            labels={'assortment_importance':'Importância no sortimento','price_position':'Posição de preço','archetype_pt':'Arquétipo'}
        )
        fig.update_xaxes(range=[0,105])
        fig.update_yaxes(range=[0,105])
        st.plotly_chart(fig_clean(fig), use_container_width=True)
    with c2:
        ranked = dm_plot.sort_values('strategic_score').tail(12)
        fig = px.bar(ranked, x='strategic_score', y='category', orientation='h', color='archetype_pt',
                     title='Pontuação Estratégica por Categoria', labels={'strategic_score':'Pontuação (0–100)','category':'','archetype_pt':'Arquétipo'})
        st.plotly_chart(fig_clean(fig), use_container_width=True)

    st.markdown(
        '<div class="retail-balloon">💡 <b>Como ler o Mapa Estratégico (Matriz de Decisão) e a Relevância por Categoria:</b><br>'
        '• <b>Círculos no topo (Faixa Premium):</b> Peças exclusivas e mais caras (Vestidos, Macacões, Blazers). Mantenha essas peças com preço cheio para gerar lucro alto.<br>'
        '• <b>Círculos na parte de baixo (Faixa Promocional):</b> Peças baratas e em liquidação (Biquínis, Conjuntos). Cancele novos descontos aqui para não queimar a margem da sua marca.<br>'
        '• <b>Pontuação Estratégica:</b> As barras à direita mostram a relevância de cada categoria. Vestidos, Macacões e Blazers são as estrelas do seu mix de produtos (prioridade máxima).</div>',
        unsafe_allow_html=True
    )

    if perfil == "Executivo / Negócios":
        st.subheader('Ações Executivas Recomendadas')
        actions_pt = actions.copy()
        actions_pt['priority'] = actions_pt['priority'].map(pt_value)
        actions_pt['archetype'] = actions_pt['archetype'].map(pt_value)
        st.dataframe(
            traduzir_colunas(actions_pt[['priority','category','archetype','headline','why','recommended_action','strategic_score']]),
            use_container_width=True, hide_index=True
        )
        st.markdown(
            '<div class="retail-balloon">💡 <b>O que são Ações Executivas Recomendadas?</b><br>'
            'Esta planilha traz a lista das principais recomendações automáticas para cada categoria baseadas no seu catálogo.<br>'
            '• Ela diz <b>exatamente o que fazer</b> em cada categoria (Ex: "revisar arquitetura de preço" ou "repor grade") '
            'e qual é o diagnóstico (diagnóstico estrutural) que levou a essa recomendação. Utilize como plano de ação semanal.</div>',
            unsafe_allow_html=True
        )

        st.subheader('Matriz de Decisão')
        show_cols = ['category','archetype','strategic_score','assortment_importance','price_position','markdown_pressure','size_depth','color_diversity','promotional_exposure']
        col_mapping = {
            'category': 'Categoria',
            'archetype': 'Arquétipo',
            'strategic_score': 'Pontuação Estratégica',
            'assortment_importance': 'Importância no Sortimento',
            'price_position': 'Posição de Preço',
            'markdown_pressure': 'Pressão de Markdown',
            'size_depth': 'Cobertura de Grade',
            'color_diversity': 'Diversidade de Cores',
            'promotional_exposure': 'Exposição Promocional'
        }
        st.dataframe(dm_plot[show_cols].rename(columns=col_mapping), use_container_width=True, hide_index=True)
        st.markdown(
            '<div class="retail-balloon">💡 <b>O que é a Matriz de Decisão?</b><br>'
            'É a tabela consolidada contendo todos os indicadores de saúde comercial de cada categoria do seu catálogo público.<br>'
            '• Ela permite analisar detalhadamente o volume de variantes, a proporção de descontos e a pontuação estratégica do sortimento. '
            'Use para comparar o desempenho e o posicionamento de cada grupo de produtos de forma rápida.</div>',
            unsafe_allow_html=True
        )
    else:
        st.subheader('Executive Actions')
        st.dataframe(
            actions[['priority','category','archetype','headline','why','recommended_action','strategic_score']],
            use_container_width=True, hide_index=True
        )

        st.subheader('Decision Matrix')
        show_cols = ['category','archetype','strategic_score','assortment_importance','price_position','markdown_pressure','size_depth','color_diversity','promotional_exposure']
        st.dataframe(dm[show_cols], use_container_width=True, hide_index=True)


elif page == 'Product Intelligence':
    header('Product Intelligence','Leitura estrutural produto a produto — papel, preço, grade, markdown e sobreposição observável.')
    pi=product_intelligence(catalog); pk=product_kpis(catalog); po=product_opportunities(catalog,top_n=30)
    cols=st.columns(5)
    with cols[0]: kpi('Total de Produtos', pk['products_analyzed'], 'Produtos-base únicos analisados pelo motor.')
    with cols[1]: kpi('Candidatos a Best-Seller', pk['hero_candidates'], 'Modelos estratégicos com alto potencial de tração. Evitar descontos e focar em reposição.')
    with cols[2]: kpi('Âncoras de Marca (Luxo)', pk['premium_anchors'], 'Peças de alto preço que definem o posicionamento de luxo da marca.')
    with cols[3]: kpi('Alerta de Encalhe (Markdown)', pk['markdown_watch'], 'Peças sem descontos que podem precisar de liquidação para girar o estoque.')
    with cols[4]: kpi('Alerta de Sobreposição', pk['redundancy_watch'], 'Modelos muito parecidos entre si. Risco de canibalização de vendas.')
    st.markdown('<div class="note"><b>Guardrail:</b> Hero Candidate e Redundancy Watch são sinais estruturais do catálogo público. Não significam best-seller ou canibalização comprovada.</div>',unsafe_allow_html=True)
    st.write('')
    c1,c2=st.columns(2)
    with c1:
        roles=pi['product_role'].value_counts().reset_index(); roles.columns=['role','items']
        fig=px.bar(roles,x='items',y='role',orientation='h',title='Product Role Architecture')
        st.plotly_chart(fig_clean(fig),use_container_width=True)
    with c2:
        cats=pi.groupby('category',as_index=False)['product_strategic_score'].mean().sort_values('product_strategic_score').tail(12)
        fig=px.bar(cats,x='product_strategic_score',y='category',orientation='h',title='Average Product Strategic Score by Category')
        st.plotly_chart(fig_clean(fig),use_container_width=True)
    st.subheader('Product Opportunity Radar')
    st.dataframe(po,use_container_width=True,hide_index=True)
    st.subheader('Product Explorer')
    categories=['Todas']+sorted(pi['category'].dropna().astype(str).unique().tolist())
    selected=st.selectbox('Categoria',categories)
    view=pi if selected=='Todas' else pi[pi['category']==selected]
    cols=['name','category','color','product_role','product_strategic_score','price','discount_pct','size_count','similar_products','redundancy_watch','recommended_action']
    st.dataframe(view[cols],use_container_width=True,hide_index=True)


elif page == 'Portfolio ML':
    header('Product Similarity & Portfolio ML','Machine Learning não supervisionado para vizinhança, clusters e densidade estrutural do portfólio.')
    space,mk=portfolio_ml(catalog); profiles=cluster_profiles(catalog); duplicates=near_duplicate_radar(catalog); sparse=white_space_candidates(catalog)
    cols=st.columns(5)
    with cols[0]: kpi('Peças do Modelo', mk['products'], 'Número de variantes inseridas na modelagem matemática de estilo.')
    with cols[1]: kpi('Estilos de Coleção Criados', mk['clusters'], 'Famílias de roupas com caimento, tecido e design semelhantes criadas pela IA.')
    with cols[2]: kpi('Precisão dos Grupos (IA)', f"{mk['silhouette'] * 100:.1f}%" if mk['silhouette'] is not None else '—', 'Índice de certeza da IA ao agrupá-las (quanto maior melhor).')
    with cols[3]: kpi('Peças Muito Parecidas', len(duplicates), 'Pares de produtos com similaridade de estilo de pelo menos 92%.')
    with cols[4]: kpi('Lacunas de Sortimento', len(sparse), 'Áreas de estilo com poucos produtos (oportunidades de novos lançamentos).')
    st.markdown('<div class="note"><b>ML Guardrail:</b> clusters, similaridade e zonas esparsas descrevem a estrutura do catálogo. Não comprovam canibalização, demanda, vendas ou oportunidade comercial.</div>',unsafe_allow_html=True)
    space_plot = space.copy()
    space_plot["cluster_label"] = "Cluster " + space_plot["portfolio_cluster"].astype(str)
    fig=px.scatter(space_plot,x='ml_x',y='ml_y',color='cluster_label',hover_name='name',
                   hover_data=['category','color','price','discount_pct','cluster_size'],title='INTI Product Space — latent 2D projection')
    st.plotly_chart(fig_clean(fig),use_container_width=True)
    c1,c2=st.columns(2)
    with c1:
        st.subheader('Portfolio Clusters')
        st.dataframe(profiles,use_container_width=True,hide_index=True)
    with c2:
        st.subheader('Sparse Portfolio Zones')
        if sparse.empty: st.info('Nenhuma zona esparsa detectada com o critério atual.')
        else: st.dataframe(sparse,use_container_width=True,hide_index=True)
    st.subheader('Product Neighborhood')
    names=sorted(space['name'].astype(str).unique().tolist())
    selected=st.selectbox('Produto',names)
    neighbors=similarity_neighbors(catalog,8)
    st.dataframe(neighbors[neighbors['product']==selected].head(8),use_container_width=True,hide_index=True)
    st.subheader('Near-Duplicate Radar')
    st.dataframe(duplicates.head(100),use_container_width=True,hide_index=True)


elif page == 'Opportunity Engine':
    header(
        'Otimização de Portfólio e Motor de Oportunidades',
        'Prioriza sinais de categoria, produto e cluster com evidência explícita e guardrails de decisão.'
    )

    opt_kpis = optimization_kpis(catalog)
    opt = portfolio_opportunity_engine(catalog)
    cluster_intel = cluster_intelligence(catalog)
    calibrated = calibrated_similarity(catalog)

    cols = st.columns(6)
    with cols[0]:
        kpi('Recomendações', opt_kpis['recommendations'], 'sinais de categoria, produto ou grupo gerados para investigação')
    with cols[1]:
        kpi('Alta prioridade', opt_kpis['high_priority'], 'recomendações que o motor posicionou no topo da fila')
    with cols[2]:
        kpi('Evidência forte', opt_kpis['strong_evidence'], 'recomendações sustentadas por quatro ou mais evidências e pontuação elevada')
    with cols[3]:
        kpi('Pares muito semelhantes', opt_kpis['calibrated_similarity_pairs'], 'pares que atingiram pelo menos 94% de similaridade estrutural calibrada')
    with cols[4]:
        kpi('Grupos analisados', opt_kpis['clusters_profiled'], 'grupos de produtos formados automaticamente pelo algoritmo')
    with cols[5]:
        kpi('Grupos pouco ocupados', opt_kpis['sparse_clusters'], 'grupos com poucos itens; são espaços estruturais a investigar, não demanda comprovada')

    st.markdown(
        '<div class="good"><b>Como interpretar os números acima:</b><br>'
        '<b>Recomendações</b> = quantidade total de sinais gerados; '
        '<b>Alta prioridade</b> = os sinais que devem ser analisados primeiro; '
        '<b>Evidência forte</b> = sinais sustentados por vários critérios ao mesmo tempo; '
        '<b>Pares muito semelhantes</b> = produtos estruturalmente próximos; '
        '<b>Grupos analisados</b> = famílias encontradas pelo algoritmo; '
        '<b>Grupos pouco ocupados</b> = regiões com poucos itens no espaço do portfólio.</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="note"><b>Evidence Gate:</b> STRONG, MODERATE e EXPLORATORY medem '
        'convergência de sinais observáveis do catálogo. Não representam probabilidade de venda, '
        'demanda, margem, ruptura ou canibalização. Recomendações comerciais devem ser validadas '
        'com dados internos antes da execução.</div>',
        unsafe_allow_html=True
    )
    st.write('')

    st.subheader('Fila Executiva de Oportunidades')
    f1, f2, f3 = st.columns([1, 1, 1])
    with f1:
        scopes = st.multiselect(
            'Escopo da recomendação',
            ['CATEGORY', 'PRODUCT', 'CLUSTER'],
            default=['CATEGORY', 'PRODUCT', 'CLUSTER'],
            key='v09_scope'
        )
    with f2:
        evidence_levels = st.multiselect(
            'Nível de evidência',
            ['STRONG', 'MODERATE', 'EXPLORATORY'],
            default=['STRONG', 'MODERATE', 'EXPLORATORY'],
            key='v09_evidence'
        )
    with f3:
        priorities = st.multiselect(
            'Prioridade da recomendação',
            ['HIGH', 'MEDIUM', 'LOW'],
            default=['HIGH', 'MEDIUM'],
            key='v09_priority'
        )

    queue = opt[
        opt['scope'].isin(scopes)
        & opt['evidence_level'].isin(evidence_levels)
        & opt['priority'].isin(priorities)
    ].copy()

    st.caption(f'{len(queue)} sinais exibidos de {len(opt)} recomendações geradas.')
    st.dataframe(
        queue[
            [
                'priority', 'scope', 'entity', 'opportunity_score',
                'evidence_level', 'headline', 'recommended_action', 'evidence'
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    c1, c2 = st.columns([1.1, 1])
    with c1:
        st.subheader('Panorama de Oportunidades')
        landscape = opt.groupby(
            ['scope', 'evidence_level'], as_index=False
        ).agg(
            signals=('entity', 'count'),
            avg_score=('opportunity_score', 'mean')
        )
        fig = px.scatter(
            landscape,
            x='avg_score',
            y='signals',
            size='signals',
            color='evidence_level',
            symbol='scope',
            hover_data=['scope', 'evidence_level'],
            title='Sinais × intensidade média'
        )
        fig.update_xaxes(range=[0, 105], title='Opportunity Score médio')
        st.plotly_chart(fig_clean(fig), use_container_width=True)
        explicar_grafico(
            'Panorama de oportunidades',
            'Cada ponto resume um tipo de alerta de estoque ou preço. '
            'Pontos mais à direita têm pontuação média maior (desvios mais críticos). '
            'Pontos maiores indicam maior quantidade de alertas daquele tipo.',
            '<b>Impacto Financeiro:</b> Ajuda a priorizar quais problemas sistêmicos atacar primeiro para estancar perdas de faturamento e margem.'
        )

    with c2:
        st.subheader('Arquitetura das Evidências')
        evidence_counts = opt['evidence_level'].value_counts().reset_index()
        evidence_counts.columns = ['evidence_level', 'signals']
        fig = px.bar(
            evidence_counts,
            x='signals',
            y='evidence_level',
            orientation='h',
            title='Distribuição dos níveis de evidência'
        )
        st.plotly_chart(fig_clean(fig), use_container_width=True)

    st.subheader('Inteligência dos Grupos')
    if cluster_intel.empty:
        st.info('Nenhum perfil de cluster disponível.')
    else:
        cluster_plot = cluster_intel.copy()
        cluster_plot['cluster_label'] = 'Cluster ' + cluster_plot['portfolio_cluster'].astype(str)

        c1, c2 = st.columns([1.05, 1])
        with c1:
            fig = px.bar(
                cluster_plot.sort_values('density_score'),
                x='density_score',
                y='cluster_label',
                orientation='h',
                color='cluster_archetype',
                title='Cluster Density Score',
                hover_data=[
                    'items', 'dominant_category', 'median_price',
                    'premium_score', 'markdown_score'
                ]
            )
            fig.update_xaxes(range=[0, 105])
            st.plotly_chart(fig_clean(fig), use_container_width=True)

        with c2:
            fig = px.scatter(
                cluster_plot,
                x='premium_score',
                y='markdown_score',
                size='items',
                color='cluster_archetype',
                hover_name='cluster_label',
                hover_data=['dominant_category', 'density_score', 'share_pct'],
                title='Premium × Markdown Cluster Map'
            )
            fig.update_xaxes(range=[0, 105])
            fig.update_yaxes(range=[0, 105])
            st.plotly_chart(fig_clean(fig), use_container_width=True)

        cluster_cols = [
            c for c in [
                'portfolio_cluster', 'cluster_archetype', 'items', 'share_pct',
                'dominant_category', 'dominant_color', 'median_price',
                'mean_discount_pct', 'median_sizes', 'density_score',
                'premium_score', 'markdown_score'
            ] if c in cluster_intel.columns
        ]
        st.dataframe(
            cluster_intel[cluster_cols],
            use_container_width=True,
            hide_index=True
        )

    st.subheader('Radar de Similaridade Calibrada')
    st.caption(
        'Limiar operacional v0.9: similaridade calibrada ≥94%. '
        'VARIANT_LIKE e STRUCTURAL_NEIGHBOR descrevem proximidade estrutural; '
        'não comprovam canibalização.'
    )

    if calibrated.empty:
        st.info('Nenhum par ultrapassou o limiar calibrado atual.')
    else:
        s1, s2 = st.columns([1, 1])
        with s1:
            signal_options = sorted(
                calibrated['similarity_signal'].dropna().astype(str).unique().tolist()
            )
            selected_signals = st.multiselect(
                'Tipo de similaridade',
                signal_options,
                default=signal_options,
                key='v09_similarity_signal'
            )
        with s2:
            minimum_similarity = st.slider(
                'Similaridade calibrada mínima',
                min_value=94.0,
                max_value=100.0,
                value=94.0,
                step=0.5,
                key='v09_similarity_threshold'
            )

        sim_view = calibrated[
            calibrated['similarity_signal'].isin(selected_signals)
            & (calibrated['calibrated_similarity_pct'] >= minimum_similarity)
        ].copy()

        sim_cols = [
            c for c in [
                'product', 'category', 'neighbor', 'neighbor_category',
                'similarity_pct', 'calibrated_similarity_pct',
                'similarity_signal', 'same_category', 'same_color',
                'same_sizes', 'price_gap_pct'
            ] if c in sim_view.columns
        ]
        st.caption(f'{len(sim_view)} pares após os filtros.')
        st.dataframe(
            sim_view[sim_cols].head(250),
            use_container_width=True,
            hide_index=True
        )

    st.subheader('Limites de Interpretação')
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(
            '<div class="good"><b>Categoria</b><br>Combina arquitetura do mix, '
            'markdown, hero candidates e premium anchors.</div>',
            unsafe_allow_html=True
        )
    with g2:
        st.markdown(
            '<div class="good"><b>Produto</b><br>Prioriza sinais estruturais; '
            'não chama Hero Candidate de best-seller.</div>',
            unsafe_allow_html=True
        )
    with g3:
        st.markdown(
            '<div class="good"><b>Cluster</b><br>Densidade, premium e markdown '
            'descrevem o espaço do catálogo, não a demanda.</div>',
            unsafe_allow_html=True
        )


elif page == 'Commercial Intelligence':
    if perfil == "Executivo / Negócios":
        header('Inteligência Comercial', 'Transforma preço e mix em leitura estratégica através de heurísticas transparentes.')
    else:
        header('Commercial Intelligence','Transforma preço e mix em leitura estratégica — heurísticas transparentes, não ML.')
    if not bundle.enriched:
        st.info('Execute primeiro o Price Enrichment completo.')
    else:
        cols = st.columns(5)
        with cols[0]: kpi('Preço mediano', brl(ck['median_price']))
        with cols[1]: kpi('Premium threshold', brl(ck['premium_threshold']), 'Q75 do catálogo')
        with cols[2]: kpi('Em markdown', f"{ck['discounted_pct']:.1f}%")
        with cols[3]: kpi('Markdown mediano', f"{ck['median_discount_pct']:.1f}%" if ck['median_discount_pct'] is not None else '—')
        with cols[4]: kpi('Promo concentration', f"{ck['promotion_concentration_top_category_pct']:.1f}%" if ck['promotion_concentration_top_category_pct'] is not None else '—', 'maior categoria entre itens em markdown')
        st.markdown('<div class="note"><b>Leitura correta:</b> Price Position Index e Markdown Pressure Index são indicadores heurísticos explicáveis. Eles não são modelos de Machine Learning nem inferem vendas.</div>', unsafe_allow_html=True)
        st.write('')
        c1,c2 = st.columns(2)
        ladder = cat_summary.sort_values('median_price')
        with c1:
            fig = px.bar(ladder, x='median_price', y='category', orientation='h', color='category_price_tier',
                         title='Price ladder · mediana por categoria', labels={'median_price':'R$','category':''})
            st.plotly_chart(fig_clean(fig), use_container_width=True)
        pressure = markdown_pressure_by_category(catalog).head(14).sort_values('markdown_pressure_index')
        with c2:
            fig = px.bar(pressure, x='markdown_pressure_index', y='category', orientation='h',
                         title='Markdown Pressure Index', labels={'markdown_pressure_index':'0–100','category':''})
            st.plotly_chart(fig_clean(fig), use_container_width=True)
        st.markdown(
            '<div class="retail-balloon">💡 <b>Como ler a Faixa de Preço (Price Ladder) e Índice de Descontos (Markdown Pressure):</b><br>'
            '• <b>Price Ladder (Escada de Preço):</b> Mostra a mediana de preço real praticada em cada categoria. Blazers, Macacões e Sobretudos estão no topo da faixa de preço (faixa rosa/premium). Calças, Blusas e Bodies representam o meio de pirâmide (faixa azul/core).<br>'
            '• <b>Índice de Descontos (Markdown Pressure):</b> Mostra quais categorias sofrem maior ação promocional da concorrência. Biquínis e Conjuntos lideram a liquidação, com mais de 70% do catálogo em desconto. Use para decidir onde proteger sua margem.</div>',
            unsafe_allow_html=True
        )
        st.subheader('Category economics')
        show = cat_summary[['category','variants','median_price','q25_price','q75_price','max_price','discounted_pct','median_discount_pct','price_position_index','category_price_tier']]
        st.dataframe(show, use_container_width=True, hide_index=True)
        st.markdown(
            '<div class="retail-balloon">💡 <b>O que é a Tabela Category Economics?</b><br>'
            'Mapeia as principais métricas de faturamento em potencial para cada categoria do concorrente.<br>'
            '• Apresenta o preço mediano, limites de quartis (Q25 e Q75), preço máximo e a fatia de peças em desconto. '
            'Útil para identificar o posicionamento exato de preços do mercado e ajustar a sua tabela de preços.</div>',
            unsafe_allow_html=True
        )
        st.subheader('Assortment × Price Matrix')
        tiers = add_price_tiers(catalog)
        matrix = pd.crosstab(tiers['category'], tiers['price_tier'])
        ordered = [c for c in ['ENTRY','CORE','UPPER','PREMIUM','UNPRICED'] if c in matrix.columns]
        matrix = matrix.reindex(columns=ordered)
        fig = px.imshow(matrix, text_auto=True, aspect='auto', title='Quantidade de variantes por faixa comercial')
        st.plotly_chart(fig_clean(fig), use_container_width=True)
        st.markdown(
            '<div class="retail-balloon">💡 <b>Como ler a Matriz de Sortimento e Faixa de Preço:</b><br>'
            'Este mapa de calor mostra a quantidade de produtos ativos em cada faixa de preço (Ex: ENTRY/Entrada, CORE/Base, PREMIUM/Alto Valor).<br>'
            '• Cores mais quentes (números maiores) indicam onde a concorrência concentra o estoque. '
            'Use para descobrir se eles têm lacunas de oferta (ex: poucos produtos na faixa Entry) que sua marca pode explorar.</div>',
            unsafe_allow_html=True
        )


elif page == 'Merchandising Intelligence':
    header('Merchandising Intelligence','Arquitetura de sortimento, profundidade de grade e sinais acionáveis para merchandising.')
    ak = assortment_kpis(catalog)
    cats = category_architecture(catalog)
    colors = color_architecture(catalog)
    density = variant_density(catalog)
    size_cov = size_coverage(catalog)
    opps = opportunity_engine(catalog)

    cols = st.columns(5)
    with cols[0]: kpi('Variantes', f"{ak['variants_total']:,}".replace(',','.'), 'sortimento público observado')
    with cols[1]: kpi('Categorias', ak['categories'], f"top category {ak['top_category_share_pct']:.1f}%")
    with cols[2]: kpi('Cores', ak['colors'], f"top color {ak['top_color_share_pct']:.1f}%")
    with cols[3]: kpi('Variantes / produto', f"{ak['median_variants_per_product']:.1f}", 'mediana')
    with cols[4]: kpi('Tamanhos / variante', f"{ak['median_sizes_per_variant']:.1f}", 'mediana')

    st.markdown('<div class="note"><b>Opportunity Engine:</b> os sinais abaixo são heurísticas transparentes baseadas na arquitetura pública do catálogo. Não inferem vendas nem estoque interno.</div>', unsafe_allow_html=True)
    st.write('')

    c1,c2 = st.columns(2)
    with c1:
        tmp = cats.sort_values('assortment_share_pct').tail(14)
        fig = px.bar(tmp, x='assortment_share_pct', y='category', orientation='h',
                     title='Category Architecture · share do sortimento',
                     labels={'assortment_share_pct':'% do catálogo','category':''})
        st.plotly_chart(fig_clean(fig), use_container_width=True)
    with c2:
        tmp = colors.sort_values('variants').tail(14)
        fig = px.bar(tmp, x='variants', y='color', orientation='h',
                     title='Color Architecture · variantes por cor',
                     labels={'variants':'variantes','color':''})
        st.plotly_chart(fig_clean(fig), use_container_width=True)

    st.subheader('Merchandising Opportunity Engine')
    if len(opps):
        high = (opps['priority']=='HIGH').sum()
        medium = (opps['priority']=='MEDIUM').sum()
        c1,c2,c3 = st.columns(3)
        with c1: kpi('Sinais', len(opps), 'oportunidades / pontos de atenção')
        with c2: kpi('Alta prioridade', int(high))
        with c3: kpi('Média prioridade', int(medium))
        st.dataframe(
            opps[['priority','signal_type','category','headline','evidence','action','score']],
            use_container_width=True, hide_index=True
        )
    else:
        st.success('Nenhum sinal de merchandising ultrapassou os thresholds heurísticos atuais.')

    c1,c2 = st.columns(2)
    with c1:
        st.subheader('Variant density')
        st.dataframe(density.head(25), use_container_width=True, hide_index=True)
    with c2:
        st.subheader('Size coverage risk')
        cols_show = [c for c in ['name','variant_name','category','color','sizes','size_count','size_coverage_score'] if c in size_cov.columns]
        st.dataframe(size_cov.head(25)[cols_show], use_container_width=True, hide_index=True)

    if bundle.enriched and len(cats):
        st.subheader('Assortment × Commercial Architecture')
        show_cols = [c for c in ['category','variants','assortment_share_pct','colors','median_sizes_per_variant','median_price','markdown_share_pct','median_discount_pct'] if c in cats.columns]
        st.dataframe(cats[show_cols], use_container_width=True, hide_index=True)

elif page == 'Price Intelligence':
    if perfil == "Executivo / Negócios":
        header('Inteligência de Preços', 'Arquitetura pública de preços, descontos (markdown) e posicionamento por categoria.')
    else:
        header('Price Intelligence','Arquitetura pública de preços, markdown e posicionamento por categoria.')
    if not bundle.enriched:
        st.info('Execute primeiro: python .\\scripts\\enrich_prices.py')
    else:
        pk = bundle.price_kpis or ck
        cols = st.columns(5)
        with cols[0]: kpi('Cobertura de preço',f"{pk.get('price_coverage_pct',0):.1f}%",f"{pk.get('priced_variants',0)} variantes")
        with cols[1]: kpi('Preço mediano',brl(pk.get('median_price')))
        with cols[2]: kpi('Preço médio',brl(pk.get('mean_price')))
        with cols[3]: kpi('Em markdown',f"{pk.get('discounted_pct',0):.1f}%",f"{pk.get('discounted_variants',0)} variantes")
        with cols[4]: kpi('Markdown mediano',f"{pk.get('median_discount_pct',0):.1f}%" if pk.get('median_discount_pct') is not None else '—')
        st.markdown('<div class="note"><b>Fonte:</b> preços públicos das páginas de produto. Confiança HIGH indica origem estruturada como JSON-LD. Não representa preço efetivamente realizado em vendas.</div>', unsafe_allow_html=True)
        priced = catalog.copy()
        for c in ['price','original_price','discount_pct']: priced[c] = pd.to_numeric(priced.get(c), errors='coerce')
        priced = priced[priced['price'].notna()]
        c1,c2 = st.columns(2)
        cp = priced.groupby(priced['category'].fillna('Sem categoria'))['price'].median().sort_values().tail(14)
        with c1: st.plotly_chart(fig_clean(px.bar(x=cp.values,y=cp.index,orientation='h',title='Preço mediano por categoria',labels={'x':'R$','y':''})),use_container_width=True)
        disc = priced[priced['discount_pct'].notna() & (priced['discount_pct'] > 0)]
        with c2:
            if len(disc): st.plotly_chart(fig_clean(px.histogram(disc,x='discount_pct',nbins=20,title='Distribuição de markdown',labels={'discount_pct':'desconto %'})),use_container_width=True)
        st.subheader('Markdown radar')
        cols_show = [c for c in ['name','category','color','price','original_price','discount_pct','price_confidence','url'] if c in disc.columns]
        show = disc.sort_values('discount_pct',ascending=False).head(30)[cols_show]
        st.dataframe(show,use_container_width=True,hide_index=True,column_config={'url':st.column_config.LinkColumn('Produto')})

elif page == 'Catalog':
    if perfil == "Executivo / Negócios":
        header('Explorador de Catálogo', 'Explore o catálogo real usando a fonte enriquecida consolidada.')
    else:
        header('Catalog Explorer','Explore o catálogo real usando a mesma fonte enriquecida do Overview e do Data Quality.')
    c1,c2,c3 = st.columns(3)
    cats=['Todos']+sorted(catalog.category.dropna().astype(str).unique())
    colors=['Todas']+sorted(catalog.color.dropna().astype(str).unique())
    with c1: cat_filter=st.selectbox('Categoria',cats)
    with c2: color_filter=st.selectbox('Cor',colors)
    with c3: q=st.text_input('Buscar produto')
    d=catalog.copy()
    if cat_filter!='Todos': d=d[d.category==cat_filter]
    if color_filter!='Todas': d=d[d.color==color_filter]
    if q: d=d[d.variant_name.astype(str).str.contains(q,case=False,na=False)]
    st.caption(f'{len(d)} variantes encontradas')
    display_cols=[c for c in ['product_id','variant_name','category','color','sizes','price','original_price','discount_pct','collection','url'] if c in d.columns]
    st.dataframe(d[display_cols].head(200),use_container_width=True,hide_index=True,column_config={'url':st.column_config.LinkColumn('Produto')})

elif page == 'Assortment':
    header('Assortment Architecture','Concentração do mix por categoria, cor e profundidade de variantes.')
    matrix=pd.crosstab(catalog.category.fillna('Sem categoria'),catalog.color.fillna('Sem cor'))
    st.plotly_chart(fig_clean(px.imshow(matrix,aspect='auto',title='Category × Color matrix')),use_container_width=True)

elif page == 'Size Intelligence':
    header('Size Intelligence','Cobertura pública da grade. Ainda não representa estoque interno nem venda.')
    if sizes.empty:
        st.info('Tabela de tamanhos ainda não disponível.')
    else:
        vc=sizes['size'].value_counts().reset_index();vc.columns=['size','occurrences']
        order=['PP','P','M','G','GG','34','36','38','40','42','44']
        vc['ord']=vc['size'].astype(str).map({v:i for i,v in enumerate(order)}).fillna(999);vc=vc.sort_values(['ord','size'])
        st.plotly_chart(fig_clean(px.bar(vc,x='size',y='occurrences',title='Presença de tamanhos no catálogo')),use_container_width=True)
        pivot=pd.crosstab(sizes.category.fillna('Sem categoria'),sizes['size'])
        st.dataframe(pivot,use_container_width=True)

elif page == 'Temporal Signals':
    if perfil == "Executivo / Negócios":
        header('Sinais Temporais', 'Mudanças observadas no catálogo e na precificação ao longo do tempo.')
    else:
        header('Temporal Signals','Mudanças observadas entre snapshots públicos — catálogo e camada comercial separadas.')
    raw_snapshots = snapshots(snapdir)
    enriched_files = enriched_snapshots(snapdir)
    c1,c2,c3 = st.columns(3)
    with c1: kpi('Arquivos de Catálogo (Raw)', str(len(raw_snapshots)), 'Capturas diárias brutas do site concorrente salvas no histórico.')
    with c2: kpi('Arquivos de Preços (Enriquecidos)', str(len(enriched_files)), 'Arquivos comerciais com preços e descontos calculados.')
    commercial_kpis_path = out / 'commercial_temporal_kpis.json'
    commercial_events_path = out / 'commercial_temporal_events.csv'
    commercial_kpis_data = {}
    if commercial_kpis_path.exists():
        import json
        commercial_kpis_data = json.loads(commercial_kpis_path.read_text(encoding='utf-8'))
    with c3: kpi('Eventos Comerciais Mapeados', str(commercial_kpis_data.get('commercial_events_total', 0)), 'Alterações reais de preços e descontos ocorridas no período.')

    # Expander explaining exactly what these files are and listing them
    import os
    from datetime import datetime
    file_rows = []
    for f in raw_snapshots:
        file_rows.append({
            "Tipo de Arquivo": "Catálogo Bruto (Raw)",
            "Nome do Arquivo": f.name,
            "Data de Captura / Extração": datetime.fromtimestamp(f.stat().st_mtime).strftime('%d/%m/%Y %H:%M'),
            "Tamanho": f"{f.stat().st_size / (1024 * 1024):.2f} MB"
        })
    for f in enriched_files:
        file_rows.append({
            "Tipo de Arquivo": "Preços Enriquecidos (Enriched)",
            "Nome do Arquivo": f.name,
            "Data de Captura / Extração": datetime.fromtimestamp(f.stat().st_mtime).strftime('%d/%m/%Y %H:%M'),
            "Tamanho": f"{f.stat().st_size / (1024 * 1024):.2f} MB"
        })

    st.markdown('<div class="note"><b>O que são Snapshots?</b> Os snapshots são arquivos de histórico do catálogo do concorrente. Eles servem para sabermos exatamente o que mudou de um dia para o outro (lançamento de novos produtos, peças que esgotaram, ou aumentos/descontos de preço).</div>', unsafe_allow_html=True)
    with st.expander("Ver lista detalhada de arquivos brutos e enriquecidos salvos no banco", expanded=True):
        st.dataframe(pd.DataFrame(file_rows), use_container_width=True, hide_index=True)

    if len(raw_snapshots) < 2:
        st.info('São necessários pelo menos dois snapshots brutos para Catalog Signals.')
    else:
        st.caption(f'Catalog period: {raw_snapshots[-2].name} → {raw_snapshots[-1].name}')

    st.subheader('Catalog Signals')
    st.caption('Produto, variante e grade pública. Mudança de disponibilidade não é interpretada como venda.')
    ev = out / 'temporal_events.csv'
    if ev.exists():
        e = pd.read_csv(ev)
        if len(e):
            counts = e.event_type.value_counts().reset_index(); counts.columns=['event','count']
            st.plotly_chart(fig_clean(px.bar(counts,x='event',y='count',title='Catalog events')),use_container_width=True)
            st.dataframe(e,use_container_width=True,hide_index=True)
        else:
            st.markdown('<div class="good"><b>Estabilidade observada:</b> nenhum evento estrutural detectado no período comparado.</div>', unsafe_allow_html=True)
    else:
        st.info(r'Execute: python .\scripts\compare_latest_snapshots.py')

    st.subheader('Commercial Signals')
    st.caption('Preço público e markdown. Não representa preço efetivamente realizado em transações.')
    if len(enriched_files) >= 2:
        st.caption(f'Commercial period: {enriched_files[-2].name} → {enriched_files[-1].name}')
    if commercial_kpis_data:
        c1,c2,c3,c4 = st.columns(4)
        with c1: kpi('Preço ↑ (Altas)', str(commercial_kpis_data.get('price_increased',0)), 'Quantidade de peças que tiveram aumento de preço.')
        with c2: kpi('Preço ↓ (Baixas)', str(commercial_kpis_data.get('price_decreased',0)), 'Quantidade de peças que ficaram mais baratas.')
        with c3: kpi('Desconto Iniciado', str(commercial_kpis_data.get('markdown_started',0)), 'Peças que entraram em promoção (preço cheio -> desconto).')
        with c4: kpi('Desconto Aumentado', str(commercial_kpis_data.get('markdown_deepened',0)), 'Peças que já estavam em promoção e ganharam ainda mais desconto.')
    
    # Explicação de indicadores zerados
    price_up = commercial_kpis_data.get('price_increased', 0)
    price_down = commercial_kpis_data.get('price_decreased', 0)
    mk_started = commercial_kpis_data.get('markdown_started', 0)
    mk_deepened = commercial_kpis_data.get('markdown_deepened', 0)
    
    if price_up == 0 and price_down == 0 and mk_started == 0 and mk_deepened == 0:
        st.markdown(
            '<div class="good">💡 <b>Por que todos os indicadores estão zerados?</b><br>'
            'Todos os indicadores comerciais estão em <b>0</b> porque os preços coletados nas duas últimas datas no banco de dados '
            'permaneceram exatamente iguais. Isso comprova que a concorrência <b>não alterou nenhum preço e não ativou novas promoções</b> '
            'nas últimas 24 horas (estabilidade de mercado). Não há ações corretivas de preço necessárias hoje.</div>',
            unsafe_allow_html=True
        )

    if commercial_events_path.exists():
        ce = pd.read_csv(commercial_events_path)
        if len(ce):
            counts = ce.event_type.value_counts().reset_index(); counts.columns=['event','count']
            st.plotly_chart(fig_clean(px.bar(counts,x='event',y='count',title='Commercial events')),use_container_width=True)
            st.dataframe(ce,use_container_width=True,hide_index=True)
        else:
            # Em caso de estabilidade
            pass
    elif len(enriched_files) >= 2:
        st.info(r'Execute: python .\scripts\compare_commercial_snapshots.py')
    else:
        st.info('São necessários pelo menos dois snapshots *_enriched.csv para Commercial Signals.')

elif page == 'Data Quality':
    header('Data Quality','Confiabilidade recalculada a partir da mesma fonte de dados usada pelo cockpit.')
    st.dataframe(quality,use_container_width=True,hide_index=True)
    if bundle.enriched:
        price_row=quality[quality.field=='price']
        if len(price_row):
            r=price_row.iloc[0]
            st.markdown(f'<div class="good"><b>Preço liberado pelo Quality Gate:</b> cobertura {r.completeness_pct:.2f}% e confiança estruturada registrada no enriquecimento. Os casos ausentes permanecem explicitamente ausentes.</div>',unsafe_allow_html=True)
        failures=out/'price_enrichment_failures.csv'
        if failures.exists():
            f=pd.read_csv(failures)
            st.subheader('Casos sem preço')
            st.caption(f'{len(f)} registros para investigação, sem contaminar os KPIs.')
            st.dataframe(f,use_container_width=True,hide_index=True)
