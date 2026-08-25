import argparse
import logging
from .collector import IntiCatalogCollector

parser = argparse.ArgumentParser(description="INTI Real Catalog Collector")
parser.add_argument("--max-products", type=int, default=None, help="Limita produtos para teste")
parser.add_argument("--verbose", action="store_true")
args = parser.parse_args()
logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
result = IntiCatalogCollector().run(args.max_products)
print("\nINTI Catalog Intelligence")
print("-" * 32)
print(f"Snapshot: {result['snapshot_id']}")
print(f"Produtos descobertos: {result['discovered']}")
print(f"Produtos coletados:   {result['collected']}")
print(f"Falhas:               {len(result['failures'])}")
print(f"CSV: {result['paths']['latest_csv']}")
