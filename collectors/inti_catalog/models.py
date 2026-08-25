from dataclasses import dataclass, asdict, field

@dataclass
class Product:
    product_id: str | None = None
    name: str | None = None
    url: str | None = None
    collection: str | None = None
    category: str | None = None
    color: str | None = None
    price: float | None = None
    original_price: float | None = None
    discount_pct: float | None = None
    sizes: list[str] = field(default_factory=list)
    description: str | None = None
    composition: str | None = None
    availability_text: str | None = None
    image_urls: list[str] = field(default_factory=list)
    source: str = "public_catalog"
    collected_at: str | None = None

    def to_dict(self):
        return asdict(self)
