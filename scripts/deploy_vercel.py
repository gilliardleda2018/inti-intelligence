import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

token = os.environ.get("VERCEL_TOKEN")
if not token:
    print("[ERRO] VERCEL_TOKEN não encontrado no .env")
    sys.exit(1)

frontend_dir = ROOT / "frontend"
print("Iniciando publicação do Dashboard no Vercel...")
cmd = f"npx vercel --token {token} --yes --prod"
res = subprocess.run(cmd, cwd=frontend_dir, shell=True, capture_output=True, text=True)

print(res.stdout)
if res.stderr:
    print("LOGS / NOTAS:")
    print(res.stderr)

if res.returncode == 0:
    print("\n[SUCESSO] Deploy no Vercel concluído com sucesso!")
else:
    print(f"\n[ERRO] Falha no deploy Vercel (Código de saída: {res.returncode})")
