import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .http import HttpClient
from .parser import discover_product_links, PRODUCT_RE
from .config import settings

def discover_from_sitemaps(client: HttpClient) -> list[str]:
    candidates = ["/sitemap.xml", "/sitemap_index.xml", "/sitemap-products.xml"]
    product_urls = set()
    sitemap_urls = set()
    for path in candidates:
        try:
            r = client.get(urljoin(settings.base_url, path))
        except Exception:
            continue
        soup = BeautifulSoup(r.text, "xml")
        locs = [x.get_text(strip=True) for x in soup.find_all("loc")]
        for loc in locs:
            if PRODUCT_RE.search(loc): product_urls.add(loc)
            elif "sitemap" in loc.lower(): sitemap_urls.add(loc)
    for sitemap in sorted(sitemap_urls):
        try:
            r = client.get(sitemap)
        except Exception:
            continue
        soup = BeautifulSoup(r.text, "xml")
        for loc in [x.get_text(strip=True) for x in soup.find_all("loc")]:
            if PRODUCT_RE.search(loc): product_urls.add(loc)
    return sorted(product_urls)

def discover_from_catalog(client: HttpClient) -> list[str]:
    r = client.get(settings.catalog_url)
    urls = set(discover_product_links(r.text, settings.base_url))
    # Some VNDA storefronts expose product cards but load subsequent cards by JS.
    # We intentionally do not reverse-engineer private endpoints here; sitemap is primary.
    return sorted(urls)

def discover_all(client: HttpClient) -> list[str]:
    urls = set(discover_from_sitemaps(client))
    urls.update(discover_from_catalog(client))
    return sorted(urls)
