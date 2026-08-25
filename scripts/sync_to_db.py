from __future__ import annotations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from inti_intelligence.data_layer import load_catalog_bundle
from inti_intelligence.database import save_catalog_to_db

def main():
    print("Iniciando sincronização do catálogo com o banco de dados...")
    
    # Load the catalog bundle (this automatically reads from CSV files if the DB table is empty or non-existent)
    bundle = load_catalog_bundle(ROOT)
    
    if bundle.catalog.empty:
        print("Erro: Nenhum dado de catálogo encontrado para sincronizar.")
        sys.exit(1)
        
    print(f"Carregado: {len(bundle.catalog)} variantes de {bundle.source_name}")
    save_catalog_to_db(bundle.catalog)
    print("Sincronização concluída com sucesso no banco de dados!")

if __name__ == '__main__':
    main()
