import os
import sys
# Removed problematic PYTHON_EXECUTABLE env var setting

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from dotenv import load_dotenv
load_dotenv()

from inti_intelligence.snowflake_db import get_snowflake_session, init_snowflake_db

def main():
    print("Iniciando publicação do Streamlit no Snowflake (SiS)...")
    
    try:
        session = get_snowflake_session()
        # Initialize DB settings, create stage if not exists
        init_snowflake_db(session)
        
        # Define stage paths
        stage_root = "@INTI_DB.PUBLIC.INTI_STAGE/dashboard"
        
        # 1. Upload dashboard/app.py to root stage
        app_py_path = (ROOT / "dashboard" / "app.py").as_posix()
        print(f"Enviando {app_py_path} para {stage_root}...")
        session.file.put(app_py_path, stage_root, auto_compress=False, overwrite=True)
        
        # Upload requirements.txt for Streamlit dependencies
        req_path = (ROOT / "requirements.txt").as_posix()
        if os.path.exists(req_path):
            print(f"Enviando {req_path} para {stage_root}...")
            session.file.put(req_path, stage_root, auto_compress=False, overwrite=True)
        
        # 2. Upload dashboard/logo.png to root stage
        logo_path = (ROOT / "dashboard" / "logo.png").as_posix()
        if os.path.exists(logo_path):
            print(f"Enviando {logo_path} para {stage_root}...")
            session.file.put(logo_path, stage_root, auto_compress=False, overwrite=True)
            
        # 3. Upload all src/inti_intelligence/*.py files to stage/src/inti_intelligence/
        src_dir = ROOT / "src" / "inti_intelligence"
        stage_src = f"{stage_root}/src/inti_intelligence"
        
        for file_path in src_dir.glob("*.py"):
            print(f"Enviando {file_path.name} para {stage_src}...")
            session.file.put(str(file_path), stage_src, auto_compress=False, overwrite=True)
            
        # 4. Create or replace the Streamlit application in Snowflake
        print("Registrando a aplicação Streamlit no Snowflake...")
        
        # Standardize query warehouse
        wh = os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
        
        sql_create_streamlit = f"""
        CREATE OR REPLACE STREAMLIT INTI_DB.PUBLIC.INTI_DASHBOARD
          ROOT_LOCATION = '{stage_root}'
          MAIN_FILE = 'app.py'
          QUERY_WAREHOUSE = '{wh}'
          COMMENT = 'Painel Executivo e Tecnico do INTI Intelligence';
        """
        session.sql(sql_create_streamlit).collect()
        
        print("\n[SUCESSO] Aplicação Streamlit publicada no Snowflake com sucesso!")
        print("Acesse-a diretamente na aba 'Streamlit' da sua conta Snowflake (Snowsight).")
        
    except Exception as e:
        print(f"\n[ERRO] Falha durante o deploy do Streamlit no Snowflake: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
