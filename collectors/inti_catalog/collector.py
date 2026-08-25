from datetime import datetime
from pathlib import Path
import logging
from .http import HttpClient
from .discovery import discover_all
from .parser import parse_product
from .storage import SnapshotStore
from .config import settings

log = logging.getLogger("inti_catalog")

class IntiCatalogCollector:
    def __init__(self, project_root: Path | None = None):
        self.root = project_root or Path(__file__).resolve().parents[2]
        self.client = HttpClient()
        self.store = SnapshotStore(self.root)

    def run(self, max_products: int | None = None):
        now = datetime.now().astimezone()
        snapshot_id = now.strftime("%Y-%m-%d_%H%M%S")
        collected_at = now.isoformat()
        urls = discover_all(self.client)
        limit = max_products if max_products is not None else settings.max_products
        if limit: urls = urls[:limit]
        log.info("Produtos descobertos: %s", len(urls))
        records, failures = [], []
        for idx, url in enumerate(urls, start=1):
            try:
                html = self.client.get(url).text
                p = parse_product(html, url, collected_at)
                records.append(p.to_dict())
                log.info("[%s/%s] %s", idx, len(urls), p.name or url)
            except Exception as exc:
                failures.append({"url": url, "error": repr(exc)})
                log.warning("Falha em %s: %s", url, exc)
        paths = self.store.save(snapshot_id, records)
        return {"snapshot_id": snapshot_id, "discovered": len(urls), "collected": len(records), "failures": failures, "paths": paths}
