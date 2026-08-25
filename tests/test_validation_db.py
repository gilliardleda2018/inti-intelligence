from __future__ import annotations
import pandas as pd
import pytest
from pydantic import ValidationError
from inti_intelligence.data_layer import validate_catalog_dataframe, CatalogRowSchema
from inti_intelligence.database import save_catalog_to_db, load_catalog_from_db, init_db, DB_URL

def test_pydantic_schema_validation_correct_data():
    correct_df = pd.DataFrame({
        'product_id': ['123', '456'],
        'name': ['Vestido', 'Calça'],
        'url': ['https://x.com/1', 'https://x.com/2'],
        'category': ['Vestidos', 'Calças'],
        'price': [150.0, 200.0]
    })
    is_valid, errors = validate_catalog_dataframe(correct_df)
    assert is_valid is True
    assert len(errors) == 0

def test_pydantic_schema_validation_corrupt_data():
    # missing required 'url' and empty name
    corrupt_df = pd.DataFrame({
        'product_id': ['123'],
        'name': [''], # name min_length is 1, so empty string should fail
        # missing url
    })
    is_valid, errors = validate_catalog_dataframe(corrupt_df)
    assert is_valid is False
    assert len(errors) > 0
    assert any("url" in err or "Colunas obrigatórias ausentes" in err for err in errors)

def test_database_persistence_sqlite_file(monkeypatch, tmp_path):
    # Force DB_URL to be a temporary SQLite file database
    db_file = tmp_path / "test_inti.db"
    monkeypatch.setattr("inti_intelligence.database.DB_URL", f"sqlite:///{db_file}")
    init_db()
    
    test_df = pd.DataFrame({
        'product_id': ['db-1', 'db-2'],
        'name': ['Prod A', 'Prod B'],
        'url': ['http://a', 'http://b'],
        'price': [99.9, 149.9]
    })
    
    save_catalog_to_db(test_df)
    loaded_df = load_catalog_from_db()
    
    assert not loaded_df.empty
    assert len(loaded_df) == 2
    assert set(loaded_df['product_id']) == {'db-1', 'db-2'}
    assert list(loaded_df[loaded_df['product_id'] == 'db-1']['price'])[0] == 99.9
