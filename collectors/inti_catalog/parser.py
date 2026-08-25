import json
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from .models import Product

PRODUCT_RE = re.compile(r"/produto/[^/?#]+-(\d+)(?:[/?#]|$)", re.I)
KNOWN_COLORS = [
    "off-white", "off white", "azul marinho", "azul índigo", "azul turquesa",
    "azul nilo", "vermelho carmim", "pink juice", "paetê dourado", "paetê prateado",
    "framboesa", "terracota", "caramelo", "castanho", "vermelho", "preto", "branco",
    "pérola", "perola", "marrom", "azul", "bege", "rosê", "rose", "fúcsia", "fucsia",
    "rosa", "pink", "avelã", "avela", "areia", "bronze", "magenta", "vanilla", "cobre"
]
CATEGORY_PREFIXES = {
    "vestido": "Vestidos", "blazer": "Blazers", "pantalona": "Calças", "calça": "Calças",
    "calca": "Calças", "short": "Shorts", "saia": "Saias", "body": "Bodies",
    "biquíni": "Biquínis", "biquini": "Biquínis", "pareô": "Pareôs", "pareo": "Pareôs",
    "macacão": "Macacões", "macacao": "Macacões", "cropped": "Croppeds", "top": "Croppeds",
    "blusa": "Blusas", "camisa": "Camisas", "casaco": "Casacos", "sobretudo": "Sobretudos",
    "saída": "Saídas", "saida": "Saídas", "conjunto": "Conjuntos",
}

def normalize_space(value: str | None) -> str | None:
    if value is None:
        return None
    return re.sub(r"\s+", " ", value).strip() or None

def parse_money(text: str | None) -> float | None:
    if not text:
        return None
    m = re.search(r"R\$\s*([\d\.]+,\d{2})", text)
    if not m:
        return None
    return float(m.group(1).replace(".", "").replace(",", "."))

def infer_product_id(url: str) -> str | None:
    m = PRODUCT_RE.search(url)
    return m.group(1) if m else None

def infer_color(name: str | None) -> str | None:
    if not name:
        return None
    lower = name.lower()
    for color in sorted(KNOWN_COLORS, key=len, reverse=True):
        if lower.endswith(color) or f" {color} " in f" {lower} ":
            return color.title().replace("Off-White", "Off White")
    return None

def infer_category(name: str | None) -> str | None:
    if not name:
        return None
    first = name.lower().split()[0]
    return CATEGORY_PREFIXES.get(first)

def discover_product_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    urls = set()
    for a in soup.select('a[href*="/produto/"]'):
        href = a.get("href")
        if not href:
            continue
        url = urljoin(base_url, href).split("#")[0]
        if PRODUCT_RE.search(url):
            urls.add(url)
    return sorted(urls)

def parse_json_ld(soup: BeautifulSoup) -> list[dict]:
    out = []
    for node in soup.select('script[type="application/ld+json"]'):
        raw = node.string or node.get_text(" ", strip=True)
        if not raw:
            continue
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list): out.extend([x for x in parsed if isinstance(x, dict)])
            elif isinstance(parsed, dict): out.append(parsed)
        except Exception:
            pass
    return out

def parse_product(html: str, url: str, collected_at: str) -> Product:
    soup = BeautifulSoup(html, "lxml")
    text = normalize_space(soup.get_text("\n", strip=True)) or ""

    h1 = soup.find("h1")
    name = normalize_space(h1.get_text(" ", strip=True) if h1 else None)
    if not name:
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        name = normalize_space(re.sub(r"\s*-\s*Inti Brand.*$", "", title, flags=re.I))

    collection = None
    if name:
        h1_node = soup.find("h1")
        if h1_node:
            candidates = []
            for el in h1_node.find_all_previous(limit=8):
                t = normalize_space(el.get_text(" ", strip=True))
                if t: candidates.append(t)
            for t in candidates:
                if re.fullmatch(r"(?:Verão|Inverno)\s+20\d{2}|Best Seller|PROGRESSIVO|50% OFF", t, re.I):
                    collection = t
                    break
    if not collection:
        m = re.search(r"\b((?:Verão|Inverno)\s+20\d{2}|Best Seller)\b", text, re.I)
        collection = m.group(1) if m else None

    sizes = []
    for node in soup.find_all(["label", "button", "option", "span", "div"]):
        t = normalize_space(node.get_text(" ", strip=True))
        if t and re.fullmatch(r"(?:PP|P|M|G|GG|U|3[4-8]|4[0-4])", t, re.I):
            sizes.append(t.upper())
    sizes = list(dict.fromkeys(sizes))

    description = None
    composition = None
    desc_button = soup.find(string=re.compile(r"^Descrição$", re.I))
    if desc_button:
        parent = desc_button.parent
        region = parent.parent if parent and parent.parent else parent
        if region:
            paras = [normalize_space(p.get_text(" ", strip=True)) for p in region.find_all("p")]
            paras = [p for p in paras if p]
            if paras: description = " ".join(paras)
    if not description:
        m = re.search(r"Descrição\s+(.*?)\s+(?:Informações|Envios em|Composição:)", text, re.I)
        if m: description = normalize_space(m.group(1))

    m = re.search(r"Composição:\s*([^\n]+?)(?=\s+(?:Modelo veste|Informações|Envios em|Tamanho|$))", text, re.I)
    if m: composition = normalize_space(m.group(1))

    images = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-lazy")
        if src and ("cdn" in src or "/products/" in src or "/produto" in src):
            images.append(urljoin(url, src))
    images = list(dict.fromkeys(images))[:20]

    price = original_price = None
    for obj in parse_json_ld(soup):
        typ = obj.get("@type")
        if typ == "Product" or (isinstance(typ, list) and "Product" in typ):
            offers = obj.get("offers")
            if isinstance(offers, dict):
                try: price = float(offers.get("price")) if offers.get("price") else price
                except Exception: pass
            if not name and obj.get("name"): name = normalize_space(str(obj["name"]))
            imgs = obj.get("image")
            if isinstance(imgs, str): images.append(imgs)
            elif isinstance(imgs, list): images.extend(str(x) for x in imgs)

    price_texts = [normalize_space(x.get_text(" ", strip=True)) for x in soup.find_all(string=re.compile(r"R\$"))]
    money = [parse_money(x) for x in price_texts]
    money = [x for x in money if x is not None]
    if money:
        if price is None: price = min(money)
        original_price = max(money)
        if original_price == price: original_price = None
    discount_pct = None
    if price and original_price and original_price > price:
        discount_pct = round((1 - price/original_price)*100, 2)

    availability_text = "public_page"
    if re.search(r"Produto Indisponível|produto indisponível", text, re.I):
        availability_text = "unavailable"
    elif re.search(r"Avise-me quando chegar", text, re.I):
        availability_text = "partial_or_variant_unavailable"
    elif re.search(r"Comprar", text, re.I):
        availability_text = "buy_action_present"

    return Product(
        product_id=infer_product_id(url), name=name, url=url, collection=collection,
        category=infer_category(name), color=infer_color(name), price=price,
        original_price=original_price, discount_pct=discount_pct, sizes=sizes,
        description=description, composition=composition,
        availability_text=availability_text, image_urls=list(dict.fromkeys(images))[:20],
        collected_at=collected_at,
    )
