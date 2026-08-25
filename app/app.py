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
from inti_intelligence.commercial_intelligence import (
    commercial_kpis, category_commercial_summary,
    markdown_pressure_by_category, add_price_tiers,
)

from inti_intelligence.visuals import load_theme, brl, kpi, fig_clean

load_theme()

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
    c_logo, c_title = st.columns([1.5, 6.5])
    with c_logo:
        import os
        logo_path = "dashboard/logo.png"
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
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=180)
st.sidebar.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)

pages = ['Overview','Commercial Intelligence','Price Intelligence','Catalog','Assortment','Size Intelligence','Temporal Signals','Data Quality']
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
    header('Temporal Signals','Mudanças observadas entre snapshots públicos do catálogo.')
    snapfiles=snapshots(snapdir)
    st.metric('Snapshots registrados',len(snapfiles))
    if len(snapfiles)<2:
        st.info('Snapshot 01 é a baseline. Não crie Snapshot 02 até a preparação temporal estar concluída.')
    ev=out/'temporal_events.csv'
    if ev.exists():
        e=pd.read_csv(ev)
        if len(e):
            counts=e.event_type.value_counts().reset_index();counts.columns=['event','count']
            st.plotly_chart(fig_clean(px.bar(counts,x='event',y='count',title='Eventos detectados')),use_container_width=True)
            st.dataframe(e,use_container_width=True,hide_index=True)

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
