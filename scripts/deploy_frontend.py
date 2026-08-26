import os
import sys
from pathlib import Path

# Ensure project root is in PYTHONPATH
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from dotenv import load_dotenv
load_dotenv()

from inti_intelligence.snowflake_db import get_snowflake_session, init_snowflake_db

def main():
    print("Iniciando upload do frontend React ao Snowflake...")
    session = get_snowflake_session()
    init_snowflake_db(session)

    # Stage where frontend will be stored
    stage_root = "@INTI_DB.PUBLIC.INTI_STAGE/dashboard/frontend"
    build_dir = (ROOT / "frontend" / "build").as_posix()
    if not os.path.isdir(build_dir):
        print(f"[ERRO] Diretório de build não encontrado: {build_dir}")
        sys.exit(1)

    # Recursively upload all files in build_dir
    for root, _, files in os.walk(build_dir):
        for f in files:
            local_path = os.path.join(root, f)
            # Compute relative path inside the stage
            rel_path = os.path.relpath(local_path, build_dir).replace('\\', '/')
            stage_path = f"{stage_root}/{rel_path}"
            print(f"Enviando {local_path} para {stage_path} ...")
            session.file.put(local_path, stage_path, auto_compress=False, overwrite=True)

    print("[SUCESSO] Frontend React publicado no Snowflake.")
    print("Acesse via URL de static site ou Crie um objeto streamlit apontando para index.html se desejar.")

if __name__ == "__main__":
    main()
