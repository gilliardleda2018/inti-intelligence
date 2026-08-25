from __future__ import annotations
import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class DBProductVariant(Base):
    __tablename__ = 'product_variants'
    
    product_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    collection = Column(String)
    category = Column(String)
    color = Column(String)
    price = Column(Float)
    original_price = Column(Float)
    discount_pct = Column(Float)
    sizes = Column(String)
    description = Column(String)
    composition = Column(String)
    availability_text = Column(String)
    image_urls = Column(String)
    source = Column(String)
    collected_at = Column(String)

# In Windows, we default database URL to a file inside C:\inti_intelligence\INTI_Intelligence\data\inti_intelligence.db
ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = ROOT_DIR / "data" / "inti_intelligence.db"
DB_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

def get_engine():
    # Make sure parent directory of sqlite db exists
    if DB_URL.startswith("sqlite:///"):
        # Remove sqlite:/// prefix to get filepath
        db_path = DB_URL.replace("sqlite:///", "")
        p = Path(db_path)
        p.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(DB_URL)

def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)

def save_catalog_to_db(df: pd.DataFrame):
    """Save a catalog DataFrame to the database, replacing previous table content."""
    init_db()
    engine = get_engine()
    if df.empty:
        return
        
    # Ensure correct columns exist and drop others before writing to DB
    columns_to_keep = [
        'product_id', 'name', 'url', 'collection', 'category', 'color',
        'price', 'original_price', 'discount_pct', 'sizes', 'description',
        'composition', 'availability_text', 'image_urls', 'source', 'collected_at'
    ]
    df_to_save = df[[c for c in columns_to_keep if c in df.columns]].copy()
    if 'product_id' in df_to_save.columns:
        df_to_save['product_id'] = df_to_save['product_id'].astype(str)
        
    df_to_save.to_sql('product_variants', con=engine, if_exists='replace', index=False)

def load_catalog_from_db() -> pd.DataFrame:
    """Load the catalog from the database table."""
    engine = get_engine()
    from sqlalchemy import inspect
    inspector = inspect(engine)
    if not inspector.has_table('product_variants'):
        return pd.DataFrame()
    return pd.read_sql_table('product_variants', con=engine)
