import getpass
from pathlib import Path

def main():
    print("=== CONFIGURAÇÃO DAS CREDENCIAIS DO SNOWFLAKE ===")
    print("Este assistente ajudará você a configurar as credenciais de acesso com segurança.")
    print("Os dados serão salvos localmente no arquivo .env na raiz do projeto.")
    print()
    
    account = input("1. Snowflake Account ID (ex: org-account ou xy12345.us-east-1): ").strip()
    user = input("2. Snowflake Usuário: ").strip()
    password = getpass.getpass("3. Snowflake Senha (a digitação ficará oculta): ").strip()
    database = input("4. Snowflake Banco de Dados (ex: INTI_DB): ").strip()
    schema = input("5. Snowflake Esquema (ex: PUBLIC): ").strip()
    warehouse = input("6. Snowflake Warehouse (ex: INTI_WH ou COMPUTE_WH): ").strip()
    role = input("7. Snowflake Role (opcional, aperte ENTER para padrão): ").strip()
    
    env_lines = [
        "# Credenciais da plataforma Snowflake (INTI Intelligence)",
        f"SNOWFLAKE_ACCOUNT={account}",
        f"SNOWFLAKE_USER={user}",
        f"SNOWFLAKE_PASSWORD={password}",
        f"SNOWFLAKE_DATABASE={database}",
        f"SNOWFLAKE_SCHEMA={schema}",
        f"SNOWFLAKE_WAREHOUSE={warehouse}"
    ]
    if role:
        env_lines.append(f"SNOWFLAKE_ROLE={role}")
        
    Path(".env").write_text("\n".join(env_lines) + "\n", encoding="utf-8")
    print("\n[OK] Arquivo .env criado e salvo com sucesso na raiz do projeto!")

if __name__ == "__main__":
    main()
