from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    base_url: str = "https://www.intibrand.com"
    catalog_url: str = "https://www.intibrand.com/all"
    timeout_seconds: int = 25
    delay_seconds: float = 1.0
    user_agent: str = (
        "Mozilla/5.0 (compatible; INTI-Intelligence-Research/0.1; "
        "+public-catalog-analysis)"
    )
    max_products: int | None = None

settings = Settings()
