from __future__ import annotations
import os
# Workaround for Windows Store Python stub – skip libc detection in Snowflake connector
os.environ["SNOWFLAKE_SKIP_LIBC_DETECTION"] = "TRUE"
# duplicate import removed
import pandas as pd
import time
from pathlib import Path
from pathlib import Path

# Load .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_snowflake_session():
    """Get the active Snowflake Snowpark session, or build a new one client-side."""
    # 1. Try to get active session (when running inside Streamlit in Snowflake)
    try:
        from snowflake.snowpark.context import get_active_session
        return get_active_session()
    except Exception:
        pass

    # 2. Build local client-side session using environment variables
    from snowflake.snowpark import Session
    
    # Check for required configs
    account = os.environ.get("SNOWFLAKE_ACCOUNT")
    user = os.environ.get("SNOWFLAKE_USER")
    password = os.environ.get("SNOWFLAKE_PASSWORD")
    
    if not account or not user:
        # Configuration is missing, we are in local development fallback
        raise ValueError("Snowflake credentials are not set in environment variables.")

    configs = {
        "account": account,
        "user": user,
        "password": password,
        "database": os.environ.get("SNOWFLAKE_DATABASE"),
        "schema": os.environ.get("SNOWFLAKE_SCHEMA"),
        "warehouse": os.environ.get("SNOWFLAKE_WAREHOUSE"),
        "role": os.environ.get("SNOWFLAKE_ROLE")
    }
    # Remove None values
    configs = {k: v for k, v in configs.items() if v is not None}
    
    return Session.builder.configs(configs).create()

def init_snowflake_db(session=None):
    """Setup the Snowflake schema, tables, and warehouse settings for cost-efficiency."""
    if session is None:
        session = get_snowflake_session()

    # (Existing init logic remains unchanged – will be kept below)

        session = get_snowflake_session()
        
    # Standardize the current warehouse to size XSMALL and suspend after 60s of inactivity to save promotional credits ($400)
    current_wh = session.get_current_warehouse()
    if current_wh:
        # Standardize warehouse size and auto-suspend
        # Quotes around identifier are safe
        session.sql(f"ALTER WAREHOUSE {current_wh} SET WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;").collect()
        print(f"Warehouse '{current_wh}' otimizado para economia de cota: XSMALL + 60s suspensão.")

    # Create Database and Schema if they don't exist
    db = os.environ.get("SNOWFLAKE_DATABASE", "INTI_DB")
    schema = os.environ.get("SNOWFLAKE_SCHEMA", "PUBLIC")
    
    session.sql(f"CREATE DATABASE IF NOT EXISTS {db};").collect()
    session.sql(f"USE DATABASE {db};").collect()
    session.sql(f"CREATE SCHEMA IF NOT EXISTS {schema};").collect()
    session.sql(f"USE SCHEMA {schema};").collect()
    
    # Create stage for streamlits
    session.sql("CREATE STAGE IF NOT EXISTS INTI_STAGE;").collect()
    print(f"Banco de dados '{db}', esquema '{schema}' e Stage 'INTI_STAGE' criados/verificados com sucesso!")

def load_catalog_from_snowflake(session=None) -> pd.DataFrame:
    """Read the product catalog table from Snowflake."""
    try:
        if session is None:
            session = get_snowflake_session()
            
        # Check if table exists
        db = os.environ.get("SNOWFLAKE_DATABASE", "INTI_DB")
        schema = os.environ.get("SNOWFLAKE_SCHEMA", "PUBLIC")
        
        tables = session.sql(f"SHOW TABLES LIKE 'PRODUCT_VARIANTS' IN SCHEMA {db}.{schema};").collect()
        if not tables:
            print("Tabela PRODUCT_VARIANTS não encontrada no Snowflake. Retornando catálogo vazio.")
            return pd.DataFrame()
            
        return session.table(f"{db}.{schema}.PRODUCT_VARIANTS").to_pandas()
    except Exception as e:
        print(f"Aviso: Falha ao carregar catálogo do Snowflake ({e}). Usando fallback local.")
        return pd.DataFrame()

def save_catalog_to_snowflake(df: pd.DataFrame, session=None):
    """Save the product catalog DataFrame to Snowflake table."""
    if session is None:
        session = get_snowflake_session()
        
    init_snowflake_db(session)
    
    db = os.environ.get("SNOWFLAKE_DATABASE", "INTI_DB")
    schema = os.environ.get("SNOWFLAKE_SCHEMA", "PUBLIC")
    
    # Write to Snowflake table
    session.create_dataframe(df).write.mode("overwrite").save_as_table(f"{db}.{schema}.PRODUCT_VARIANTS")
    print(f"Salvo com sucesso {len(df)} linhas na tabela {db}.{schema}.PRODUCT_VARIANTS!")
