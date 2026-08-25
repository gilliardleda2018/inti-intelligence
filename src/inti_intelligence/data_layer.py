from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import pandas as pd
from pydantic import BaseModel, Field, ValidationError
from typing import Optional


@dataclass(frozen=True)
class CatalogBundle:
    catalog: pd.DataFrame
    variants: pd.DataFrame
    sizes: pd.DataFrame
    quality: pd.DataFrame
    catalog_kpis: dict
    price_kpis: dict
    source_name: str
    enriched: bool
    validation_errors: list[str]


class CatalogRowSchema(BaseModel):
    product_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    url: str = Field(..., min_length=1)
    collection: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    discount_pct: Optional[float] = None
    sizes: Optional[str] = ""
    description: Optional[str] = None
    composition: Optional[str] = None
    availability_text: Optional[str] = None
    image_urls: Optional[str] = None
    source: Optional[str] = None
    collected_at: Optional[str] = None


def validate_catalog_dataframe(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """Validate a catalog DataFrame against CatalogRowSchema.
    
    Returns:
        (is_valid, list_of_error_messages)
    """
    errors = []
    if df.empty:
        return True, errors
        
    required = ["product_id", "name", "url"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        errors.append(f"Colunas obrigatórias ausentes no CSV: {missing}")
        return False, errors
        
    records = df.to_dict(orient="records")
    for idx, record in enumerate(records):
        cleaned = {k: (None if pd.isna(v) else v) for k, v in record.items()}
        if cleaned.get("product_id") is not None:
            cleaned["product_id"] = str(cleaned["product_id"])
        try:
            CatalogRowSchema(**cleaned)
        except ValidationError as e:
            err_details = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            errors.append(f"Linha {idx+2} (ID: {cleaned.get('product_id')}): {', '.join(err_details)}")
            if len(errors) >= 10:
                errors.append("... mais erros de validação ocultados no resumo.")
                break
                
    return len(errors) == 0, errors


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))


def build_quality_report(catalog: pd.DataFrame) -> pd.DataFrame:
    """Build the cockpit quality view from the active source of truth.

    This intentionally recalculates quality from the enriched dataset when it is
    available, so the Overview/Data Quality pages cannot remain stuck on the
    pre-enrichment Snapshot 01 report.
    """
    fields = [
        ('product_id', True), ('name', True), ('url', True), ('collection', True),
        ('category', True), ('color', True), ('price', False),
        ('original_price', False), ('discount_pct', False), ('sizes', True),
    ]
    n = len(catalog)
    rows = []
    for field, critical in fields:
        if field in catalog.columns:
            s = catalog[field]
            non_null = int(s.notna().sum())
            if s.dtype == object:
                non_null = int((s.notna() & s.astype(str).str.strip().ne('')).sum())
        else:
            non_null = 0
        missing = max(0, n - non_null)
        completeness = round(100 * non_null / n, 2) if n else 0.0
        if field == 'price':
            confidence = catalog.get('price_confidence', pd.Series(index=catalog.index, dtype='object'))
            high = int((confidence == 'HIGH').sum()) if len(catalog) else 0
            high_pct = round(100 * high / non_null, 2) if non_null else 0.0
            trust = 'GOOD' if completeness >= 95 and high_pct >= 95 else ('PARTIAL' if non_null else 'MISSING')
        elif completeness >= 95:
            trust = 'GOOD'
        elif non_null:
            trust = 'PARTIAL'
        else:
            trust = 'MISSING'
        rows.append({
            'field': field, 'rows': n, 'non_null': non_null, 'missing': missing,
            'completeness_pct': completeness, 'critical': critical, 'trust': trust,
        })
    return pd.DataFrame(rows)


def load_catalog_bundle(root: Path) -> CatalogBundle:
    out = root / 'data' / 'output'
    enriched_path = out / 'catalog_enriched_latest.csv'
    raw_snapshot = root / 'data' / 'snapshots' / 'snapshot_01_2026-08-24.csv'
    variants_path = out / 'product_variants.csv'
    sizes_path = out / 'variant_sizes.csv'

    catalog = None
    source_name = None
    enriched = False

    # 1. Try loading from Snowflake database
    try:
        from .snowflake_db import load_catalog_from_snowflake
        sf_catalog = load_catalog_from_snowflake()
        if sf_catalog is not None and not sf_catalog.empty:
            catalog = sf_catalog
            source_name = 'Snowflake (table: PRODUCT_VARIANTS)'
            # Mark enriched if we have at least one observed price in catalog
            enriched = 'price' in catalog.columns and catalog['price'].notna().any()
    except Exception as e:
        print(f"Snowflake load failed: {e}")

    # 2. Try loading from SQLite database (local fallback)
    if catalog is None:
        try:
            from .database import load_catalog_from_db
            db_catalog = load_catalog_from_db()
            if not db_catalog.empty:
                catalog = db_catalog
                source_name = 'SQLite database (table: product_variants)'
                enriched = 'price' in catalog.columns and catalog['price'].notna().any()
            else:
                raise Exception("Database table is empty")
        except Exception:
            pass

    # 3. Fallback to local CSV files
    if catalog is None:
        if enriched_path.exists():
            catalog = _read_csv(enriched_path)
            source_name = 'catalog_enriched_latest.csv'
            enriched = True
        elif raw_snapshot.exists():
            catalog = _read_csv(raw_snapshot)
            source_name = raw_snapshot.name
            enriched = False
        else:
            catalog = _read_csv(variants_path)
            source_name = variants_path.name
            enriched = False

    # Validate data integrity with Pydantic
    is_valid, validation_errors = validate_catalog_dataframe(catalog)

    variants = _read_csv(variants_path)
    sizes = _read_csv(sizes_path)
    quality = build_quality_report(catalog)
    catalog_kpis = _read_json(out / 'catalog_kpis.json')
    price_kpis = _read_json(out / 'price_kpis.json') if enriched else {}

    return CatalogBundle(
        catalog=catalog,
        variants=variants,
        sizes=sizes,
        quality=quality,
        catalog_kpis=catalog_kpis,
        price_kpis=price_kpis,
        source_name=source_name,
        enriched=enriched,
        validation_errors=validation_errors,
    )
