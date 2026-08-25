from __future__ import annotations
import streamlit as st
import pandas as pd

CSS_STYLE = '''<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Outfit:wght@200;300;400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,500;1,400&display=swap');

:root {
    --bg: #FAF9F6;
    --ink: #1C1A17;
    --muted: #8E877B;
    --line: #E8E5DD;
    --paper: #FFFFFF;
    --accent: #D25D38;
    --soft: #F6F3EB;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--ink) !important;
}

[data-testid="stSidebar"] {
    background-color: #141311 !important;
    border-right: 1px solid #282522;
}

[data-testid="stSidebar"] * {
    color: #FAF9F6 !important;
    font-family: 'Inter', sans-serif !important;
}

h1, h2, h3, .stSubheader, .inti-title {
    font-family: 'Playfair Display', serif !important;
    font-weight: 400 !important;
    color: var(--ink);
}

.inti-title {
    font-size: 2.85rem;
    font-style: italic;
    line-height: 1.1;
    margin: 0 0 0.5rem 0;
}

.block-container {
    max-width: 1400px;
    padding-top: 5.5rem !important;
    padding-bottom: 2rem;
}

.inti-kicker {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.3rem;
}

.inti-rule {
    height: 1px;
    background: var(--line);
    margin: 1rem 0 1.5rem 0;
}

.kpi {
    background: var(--paper);
    border: 1px solid var(--line);
    border-top: 3px solid var(--accent);
    padding: 1.5rem 1.4rem;
    border-radius: 8px;
    min-height: 146px;
    box-shadow: 0 4px 20px rgba(26,24,20,0.02);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.kpi:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(210,93,56,0.08);
    border-color: var(--accent);
}

.kpi .label {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
}

.kpi .value {
    font-family: 'Outfit', sans-serif;
    font-size: 2.4rem;
    font-weight: 300;
    line-height: 1.0;
    margin-top: 0.5rem;
    color: var(--ink);
}

.kpi .sub {
    font-size: 0.86rem;
    line-height: 1.35;
    color: #2F2E2C; /* Texto mais escuro para melhor leitura */
    margin-top: 0.5rem;
}

.note {
    border-left: 2px solid var(--accent);
    background: var(--soft);
    padding: 0.8rem 1rem;
    color: #000000; /* Preto puro */
    font-size: 0.92rem; /* Fonte maior */
    border-radius: 0 4px 4px 0;
    margin-bottom: 1rem;
}

.good {
    border-left: 2px solid #5E7454;
    background: #E8ECE3;
    padding: 0.8rem 1rem;
    color: #000000; /* Preto puro */
    font-size: 0.92rem; /* Fonte maior */
    border-radius: 0 4px 4px 0;
    margin-bottom: 1rem;
}

.retail-balloon {
    background: #FCFAF6;
    border: 1px dashed #D0C9BE;
    border-radius: 8px;
    padding: 0.95rem;
    font-size: 0.86rem;
    line-height: 1.45;
    color: #000000;
    margin-top: 0.8rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 12px rgba(26,24,20,0.01);
}

.product-card {
    background: var(--paper);
    border: 1px solid var(--line);
    padding: 0.9rem;
    border-radius: 8px;
    height: 100%;
    box-shadow: 0 4px 15px rgba(26,24,20,0.01);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.product-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(210,93,56,0.06);
    border-color: var(--accent);
}

.product-card img {
    width: 100%;
    aspect-ratio: 3/4;
    object-fit: cover;
    border-radius: 6px;
    background: #F6F3EB;
}

.product-card .name {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    font-style: italic;
    margin-top: 0.6rem;
    color: var(--ink);
}

.product-card .meta {
    font-size: 0.75rem;
    color: var(--muted);
}

.source-pill {
    display: inline-block;
    border: 1px solid var(--line);
    background: var(--soft);
    padding: 0.25rem 0.5rem;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.05em;
    color: var(--muted);
    border-radius: 4px;
    margin-bottom: 1rem;
}

.action-card {
    background: linear-gradient(145deg, #FFFFFF 0%, #FAF9F6 100%);
    border: 1px solid var(--line);
    border-left: 4px solid var(--accent);
    padding: 1.4rem;
    margin-bottom: 1.2rem;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(26,24,20,0.02);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.action-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 30px rgba(210,93,56,0.07);
}

.action-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.4rem;
}

.action-badge-high {
    background: var(--accent);
    color: #FFFFFF !important;
    padding: 0.15rem 0.4rem;
    font-size: 0.62rem;
    font-weight: 600;
    border-radius: 2px;
    text-transform: uppercase;
}

.action-badge-medium {
    background: var(--soft);
    color: var(--ink) !important;
    padding: 0.15rem 0.4rem;
    font-size: 0.62rem;
    font-weight: 600;
    border-radius: 2px;
    text-transform: uppercase;
}

.action-card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem;
    font-weight: 500;
    color: var(--ink);
}

.action-card-text {
    font-size: 0.92rem; /* Fonte maior */
    color: #111111; /* Quase preto puro */
}

.action-card-evidence {
    font-size: 0.78rem; /* Fonte maior */
    color: var(--muted);
    margin-top: 0.4rem;
    border-top: 1px solid var(--line);
    padding-top: 0.4rem;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: var(--bg);
}
::-webkit-scrollbar-thumb {
    background: var(--line);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: var(--accent);
}
</style>'''

def load_theme():
    st.markdown(CSS_STYLE, unsafe_allow_html=True)

def brl(v):
    if v is None or pd.isna(v): return '—'
    return f'R$ {float(v):,.2f}'.replace(',', 'X').replace('.', ',').replace('X','.')

def kpi(label, value, sub=''):
    significado = f'<div class="sub"><b>Significa:</b> {sub}</div>' if sub else ''
    st.markdown(
        f'<div class="kpi"><div class="label">{label}</div>'
        f'<div class="value">{value}</div>{significado}</div>',
        unsafe_allow_html=True
    )

def explicar_grafico(titulo, leitura, atencao=None):
    t=f'<div class="note"><b>Como ler — {titulo}:</b> {leitura}'
    if atencao:t+=f'<br><b>Importante:</b> {atencao}'
    st.markdown(t+'</div>',unsafe_allow_html=True)

def fig_clean(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#44423E', size=11),
        title_font=dict(family='Playfair Display', color='#1C1A17', size=16),
        margin=dict(l=15, r=20, t=58, b=20),
        legend=dict(
            font=dict(color='#1C1A17', size=11),
            title_font=dict(color='#1C1A17', size=11),
            bgcolor='rgba(255,255,255,0.96)',
            bordercolor='#E8E5DD',
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor='#FFFFFF',
            bordercolor='#E8E5DD',
            font=dict(color='#1C1A17', size=11)
        )
    )
    fig.update_xaxes(
        showgrid=False, zeroline=False,
        tickfont=dict(color='#44423E', size=11),
        title_font=dict(color='#44423E', size=12),
        linecolor='#E8E5DD'
    )
    fig.update_yaxes(
        gridcolor='#F6F3EB', zeroline=False,
        tickfont=dict(color='#44423E', size=11),
        title_font=dict(color='#44423E', size=12),
        linecolor='#E8E5DD'
    )
    try:
        fig.update_coloraxes(
            colorbar_tickfont=dict(color='#44423E', size=10),
            colorbar_title_font=dict(color='#44423E', size=11)
        )
    except Exception:
        pass
    return fig
