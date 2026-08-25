from __future__ import annotations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from dotenv import load_dotenv
load_dotenv()

from inti_intelligence.data_layer import load_catalog_bundle
from inti_intelligence.snowflake_db import save_catalog_to_snowflake

def main():
    print("Iniciando upload e sincronização com a plataforma Snowflake...")
    
    # Load catalog bundle from local CSV files
    bundle = load_catalog_bundle(ROOT)
    
    if bundle.catalog.empty:
        print("Erro: Catálogo local vazio. Carga cancelada.")
        sys.exit(1)
        
    print(f"Lendo catálogo local: {len(bundle.catalog)} itens de {bundle.source_name}")
    
    try:
        save_catalog_to_snowflake(bundle.catalog)
        print("Sincronização concluída com sucesso no Snowflake (tabela: PRODUCT_VARIANTS)!")
    except Exception as e:
        print(f"Erro durante sincronização com Snowflake: {e}")
        print("Verifique se as credenciais no arquivo .env ou variáveis de ambiente estão corretas.")
        sys.exit(1)

if __name__ == '__main__':
    main()
