from pathlib import Path
import sys
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

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

st.set_page_config(page_title='INTI Intelligence', page_icon='◼', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
:root{--bg:#F5F2EC;--ink:#171717;--muted:#77736D;--line:#D8D2C7;--paper:#FCFAF6;--accent:#A1492D;--soft:#EDE7DD}
.stApp{background:var(--bg);color:var(--ink)}
[data-testid="stSidebar"]{background:#171717}
[data-testid="stSidebar"] *{color:#F5F2EC!important}
h1,h2,h3{font-family:Georgia,'Times New Roman',serif!important;letter-spacing:-.03em}
.block-container{max-width:1500px;padding-top:2.2rem}
.inti-kicker{font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);margin-bottom:.35rem}
.inti-title{font-family:Georgia,serif;font-size:3.25rem;line-height:.98;margin:0 0 .6rem 0}
.inti-rule{height:1px;background:var(--line);margin:1.3rem 0 1.8rem}
.kpi{background:var(--paper);border:1px solid var(--line);padding:1.15rem 1.2rem;min-height:120px}
.kpi .label{font-size:.68rem;letter-spacing:.13em;text-transform:uppercase;color:var(--muted)}
.kpi .value{font-family:Georgia,serif;font-size:2.45rem;margin-top:.25rem}.kpi .sub{font-size:.78rem;color:var(--muted)}
.note{border-left:3px solid var(--accent);background:#EFE8DE;padding:.9rem 1rem;color:#3c3935}
.good{border-left:3px solid #5E7454;background:#E7ECE2;padding:.9rem 1rem;color:#31362e}
.product-card{background:var(--paper);border:1px solid var(--line);padding:.7rem;height:100%}.product-card img{width:100%;aspect-ratio:3/4;object-fit:cover;background:#e8e4dd}
.product-card .name{font-family:Georgia,serif;font-size:1.03rem;margin-top:.6rem}.product-card .meta{font-size:.73rem;color:var(--muted)}
.source-pill{display:inline-block;border:1px solid var(--line);background:var(--paper);padding:.35rem .55rem;font-size:.72rem;color:var(--muted);margin-bottom:1rem}
</style>''', unsafe_allow_html=True)

bundle = load_catalog_bundle(ROOT)
catalog = bundle.catalog.copy()
variants = bundle.variants.copy()
sizes = bundle.sizes.copy()
quality = bundle.quality.copy()
out = ROOT / 'data' / 'output'
snapdir = ROOT / 'data' / 'snapshots'

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


def header(title, sub):
    st.markdown(
        f'<div class="inti-kicker">INTI INTELLIGENCE · DECISION SYSTEM</div>'
        f'<div class="inti-title">{title}</div><div style="color:#77736D">{sub}</div>'
        f'<div class="inti-rule"></div>', unsafe_allow_html=True)
    st.markdown(f'<span class="source-pill">SOURCE OF TRUTH · {bundle.source_name}</span>', unsafe_allow_html=True)


def kpi(label, value, sub=''):
    st.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div><div class="sub">{sub}</div></div>', unsafe_allow_html=True)


def brl(v):
    if v is None or pd.isna(v): return '—'
    return f'R$ {float(v):,.2f}'.replace(',', 'X').replace('.', ',').replace('X','.')


def fig_clean(fig):
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(family='Arial', color='#38342f'), margin=dict(l=10,r=10,t=45,b=10))
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor='#DDD7CC', zeroline=False)
    return fig


def safe_image(row):
    val = row.get('image_urls')
    if pd.notna(val) and str(val).strip(): return str(val).split('|')[0]
    return ''

pages = ['Overview','Decision Intelligence','Product Intelligence','Portfolio ML','Commercial Intelligence','Merchandising Intelligence','Price Intelligence','Catalog','Assortment','Size Intelligence','Temporal Signals','Data Quality']
page = st.sidebar.radio('INTI Intelligence', pages)
st.sidebar.caption('Single Source of Truth ativo')
st.sidebar.caption(f'Fonte: {bundle.source_name}')

ck = commercial_kpis(catalog) if bundle.enriched else {}
cat_summary = category_commercial_summary(catalog) if bundle.enriched else pd.DataFrame()

if page == 'Overview':
    header('Collection Intelligence','Visão executiva do catálogo público enriquecido, com quality gates explícitos.')
    base_kpis = bundle.catalog_kpis
    cols = st.columns(4)
    with cols[0]: kpi('Produtos-base', f"{base_kpis.get('products_base',401):,}".replace(',','.'), 'modelos normalizados')
    with cols[1]: kpi('Variantes', f"{len(catalog):,}".replace(',','.'), 'catálogo público observado')
    with cols[2]: kpi('Cobertura de preço', f"{ck.get('price_coverage_pct',0):.1f}%" if bundle.enriched else '—', 'fonte estruturada quando disponível')
    with cols[3]: kpi('Preço mediano', brl(ck.get('median_price')) if bundle.enriched else '—', 'preço público atual')
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
    if bundle.enriched and len(cat_summary):
        st.subheader('Commercial pulse')
        c1,c2,c3 = st.columns(3)
        with c1: kpi('Catálogo em markdown', f"{ck['discounted_pct']:.1f}%", 'share das variantes precificadas')
        with c2: kpi('Markdown mediano', f"{ck['median_discount_pct']:.1f}%" if ck['median_discount_pct'] is not None else '—', 'profundidade típica quando há desconto')
        with c3: kpi('Premium threshold', brl(ck['premium_threshold']), 'quartil superior de preço')


elif page == 'Decision Intelligence':
    header('Decision Intelligence','Mapa estratégico do catálogo público — importância, preço, pressão promocional, grade e diversidade.')
    dm = category_decision_map(catalog)
    dk = decision_kpis(catalog)
    actions = executive_actions(catalog, top_n=10)

    cols = st.columns(5)
    with cols[0]: kpi('Categorias', dk['categories'])
    with cols[1]: kpi('Premium Core', dk['premium_core'], 'arquétipo estratégico')
    with cols[2]: kpi('Promotion Pressure', dk['promotion_pressure'], 'atenção promocional')
    with cols[3]: kpi('Niche Premium', dk['niche_premium'])
    with cols[4]: kpi('Top strategic', dk['top_strategic_category'] or '—', f"{dk['top_strategic_score'] or 0:.1f}/100")

    st.markdown('<div class="note"><b>Importante:</b> o Strategic Score mede relevância estratégica observável no catálogo público. Não é previsão de vendas, margem ou demanda.</div>', unsafe_allow_html=True)
    st.write('')

    c1,c2 = st.columns([1.15,1])
    with c1:
        fig = px.scatter(
            dm, x='assortment_importance', y='price_position',
            size='variants', color='archetype', hover_name='category',
            hover_data=['markdown_pressure','size_depth','color_diversity','strategic_score'],
            title='INTI Category Strategic Map',
            labels={'assortment_importance':'Importância no sortimento','price_position':'Posição de preço'}
        )
        fig.update_xaxes(range=[0,105])
        fig.update_yaxes(range=[0,105])
        st.plotly_chart(fig_clean(fig), use_container_width=True)
    with c2:
        ranked = dm.sort_values('strategic_score').tail(12)
        fig = px.bar(ranked, x='strategic_score', y='category', orientation='h', color='archetype',
                     title='Category Strategic Score', labels={'strategic_score':'0–100','category':''})
        st.plotly_chart(fig_clean(fig), use_container_width=True)

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
    with cols[0]: kpi('Itens analisados',pk['products_analyzed'])
    with cols[1]: kpi('Hero Candidates',pk['hero_candidates'],'requer validação com vendas')
    with cols[2]: kpi('Premium Anchors',pk['premium_anchors'])
    with cols[3]: kpi('Markdown Watch',pk['markdown_watch'])
    with cols[4]: kpi('Redundancy Watch',pk['redundancy_watch'],'sobreposição estrutural')
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
    with cols[0]: kpi('Produtos',mk['products'])
    with cols[1]: kpi('Clusters',mk['clusters'])
    with cols[2]: kpi('Silhouette',mk['silhouette'] if mk['silhouette'] is not None else '—','qualidade interna')
    with cols[3]: kpi('Near-duplicate pairs',len(duplicates),'similaridade ≥92%')
    with cols[4]: kpi('Sparse zones',len(sparse),'não implica demanda')
    st.markdown('<div class="note"><b>ML Guardrail:</b> clusters, similaridade e zonas esparsas descrevem a estrutura do catálogo. Não comprovam canibalização, demanda, vendas ou oportunidade comercial.</div>',unsafe_allow_html=True)
    fig=px.scatter(space,x='ml_x',y='ml_y',color=space['portfolio_cluster'].astype(str),hover_name='name',
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

elif page == 'Commercial Intelligence':
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
        st.subheader('Category economics')
        show = cat_summary[['category','variants','median_price','q25_price','q75_price','max_price','discounted_pct','median_discount_pct','price_position_index','category_price_tier']]
        st.dataframe(show, use_container_width=True, hide_index=True)
        st.subheader('Assortment × Price Matrix')
        tiers = add_price_tiers(catalog)
        matrix = pd.crosstab(tiers['category'], tiers['price_tier'])
        ordered = [c for c in ['ENTRY','CORE','UPPER','PREMIUM','UNPRICED'] if c in matrix.columns]
        matrix = matrix.reindex(columns=ordered)
        fig = px.imshow(matrix, text_auto=True, aspect='auto', title='Quantidade de variantes por faixa comercial')
        st.plotly_chart(fig_clean(fig), use_container_width=True)


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
    header('Temporal Signals','Mudanças observadas entre snapshots públicos — catálogo e camada comercial separadas.')
    raw_snapshots = snapshots(snapdir)
    enriched_files = enriched_snapshots(snapdir)
    c1,c2,c3 = st.columns(3)
    with c1: kpi('Snapshots de catálogo', str(len(raw_snapshots)), 'arquivos brutos preservados')
    with c2: kpi('Snapshots enriquecidos', str(len(enriched_files)), 'estados comerciais preservados')
    commercial_kpis_path = out / 'commercial_temporal_kpis.json'
    commercial_events_path = out / 'commercial_temporal_events.csv'
    commercial_kpis_data = {}
    if commercial_kpis_path.exists():
        import json
        commercial_kpis_data = json.loads(commercial_kpis_path.read_text(encoding='utf-8'))
    with c3: kpi('Eventos comerciais', str(commercial_kpis_data.get('commercial_events_total', 0)), 'mudanças observáveis de preço/markdown')

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
        with c1: kpi('Preço ↑', str(commercial_kpis_data.get('price_increased',0)))
        with c2: kpi('Preço ↓', str(commercial_kpis_data.get('price_decreased',0)))
        with c3: kpi('Markdown iniciado', str(commercial_kpis_data.get('markdown_started',0)))
        with c4: kpi('Markdown aprofundado', str(commercial_kpis_data.get('markdown_deepened',0)))
    if commercial_events_path.exists():
        ce = pd.read_csv(commercial_events_path)
        if len(ce):
            counts = ce.event_type.value_counts().reset_index(); counts.columns=['event','count']
            st.plotly_chart(fig_clean(px.bar(counts,x='event',y='count',title='Commercial events')),use_container_width=True)
            st.dataframe(ce,use_container_width=True,hide_index=True)
        else:
            st.markdown('<div class="good"><b>Estabilidade comercial observada:</b> nenhum preço ou markdown mudou entre os dois snapshots enriquecidos.</div>', unsafe_allow_html=True)
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
