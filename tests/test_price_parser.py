import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from inti_intelligence.price_parser import parse_price_html

def test_visible_sale_price():
    html='<main><h1>Vestido</h1><div><s>R$ 1.489,00</s><strong>R$ 1.191,20</strong></div></main>'
    r=parse_price_html(html)
    assert r.price==1191.20
    assert r.original_price==1489.0
    assert round(r.discount_pct,1)==20.0

def test_jsonld_price():
    html='<script type="application/ld+json">{"@type":"Product","offers":{"@type":"Offer","price":"1699.00"}}</script>'
    r=parse_price_html(html)
    assert r.price==1699.0 and r.confidence=='HIGH'
