import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from dotenv import load_dotenv
load_dotenv()

from inti_intelligence.snowflake_db import get_snowflake_session

def main():
    print("Concedendo permissões e configurando acesso ao Dashboard no Snowflake...")
    session = get_snowflake_session()
    
    statements = [
        "GRANT USAGE ON DATABASE INTI_DB TO ROLE PUBLIC;",
        "GRANT USAGE ON SCHEMA INTI_DB.PUBLIC TO ROLE PUBLIC;",
        "GRANT READ ON STAGE INTI_DB.PUBLIC.INTI_STAGE TO ROLE PUBLIC;"
    ]
    
    for stmt in statements:
        try:
            print(f"Executando: {stmt}")
            session.sql(stmt).collect()
            print(" -> Sucesso.")
        except Exception as e:
            print(f" -> Aviso: {e}")

    print("\n[CONCLUÍDO] Permissões atualizadas com sucesso!")

if __name__ == "__main__":
    main()
