from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import math
import pandas as pd

EVENT_COLUMNS = [
    'event_type', 'product_id', 'name', 'category', 'color',
    'old_value', 'new_value', 'delta', 'detail'
]


def _num(value):
    try:
        if pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _same(a, b, tol=1e-9):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tol)


def _sale_state(row) -> bool:
    price = _num(row.get('price'))
    original = _num(row.get('original_price'))
    discount = _num(row.get('discount_pct'))
    return bool(
        price is not None and (
            (original is not None and original > price + 1e-9)
            or (discount is not None and discount > 0.01)
        )
    )


def _discount(row):
    d = _num(row.get('discount_pct'))
    if d is not None:
        return d
    p = _num(row.get('price'))
    o = _num(row.get('original_price'))
    if p is not None and o is not None and o > 0 and o > p:
        return 100 * (o - p) / o
    return None


def _prep(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    if 'product_id' not in d.columns:
        raise ValueError('Snapshot enriquecido sem coluna product_id.')
    d['product_id'] = d['product_id'].astype(str)
    # Defensive dedupe: keep last occurrence, but do not invent a compound key.
    d = d.drop_duplicates(subset=['product_id'], keep='last')
    for col in ('price', 'original_price', 'discount_pct'):
        d[col] = pd.to_numeric(d.get(col), errors='coerce')
    return d.set_index('product_id', drop=False)


def compare_commercial_snapshots(old: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    """Compare two enriched public catalog snapshots.

    This function only reports observable public price/markdown changes. It does
    not infer sales, demand, stock movement or realized transaction prices.
    """
    a, b = _prep(old), _prep(new)
    events = []

    def add(event_type, pid, row, old_value, new_value, delta, detail):
        events.append({
            'event_type': event_type,
            'product_id': pid,
            'name': row.get('name'),
            'category': row.get('category'),
            'color': row.get('color'),
            'old_value': old_value,
            'new_value': new_value,
            'delta': delta,
            'detail': detail,
        })

    for pid in sorted(set(a.index) & set(b.index)):
        x, y = a.loc[pid], b.loc[pid]
        op, np = _num(x.get('price')), _num(y.get('price'))
        od, nd = _discount(x), _discount(y)
        old_sale, new_sale = _sale_state(x), _sale_state(y)

        if op is not None and np is not None and not _same(op, np):
            delta = np - op
            pct = (100 * delta / op) if op else None
            event = 'PRICE_INCREASED' if delta > 0 else 'PRICE_DECREASED'
            detail = f'Preço público: {op:.2f} -> {np:.2f}'
            if pct is not None:
                detail += f' ({pct:+.2f}%)'
            add(event, pid, y, op, np, round(delta, 2), detail)

        if (not old_sale) and new_sale:
            add('MARKDOWN_STARTED', pid, y, od, nd, None if od is None or nd is None else round(nd-od, 2),
                'Produto passou a exibir markdown no catálogo público')
            add('ENTERED_SALE', pid, y, op, np, None if op is None or np is None else round(np-op, 2),
                'Produto entrou em condição promocional observável')
        elif old_sale and (not new_sale):
            add('MARKDOWN_ENDED', pid, y, od, nd, None if od is None or nd is None else round(nd-od, 2),
                'Markdown deixou de ser exibido no catálogo público')
            add('LEFT_SALE', pid, y, op, np, None if op is None or np is None else round(np-op, 2),
                'Produto deixou a condição promocional observável')
        elif old_sale and new_sale and od is not None and nd is not None and not _same(od, nd, tol=0.01):
            delta = nd - od
            event = 'MARKDOWN_DEEPENED' if delta > 0 else 'MARKDOWN_REDUCED'
            detail = f'Markdown público: {od:.2f}% -> {nd:.2f}% ({delta:+.2f} p.p.)'
            add(event, pid, y, round(od, 2), round(nd, 2), round(delta, 2), detail)

    return pd.DataFrame(events, columns=EVENT_COLUMNS)


def commercial_temporal_kpis(old: pd.DataFrame, new: pd.DataFrame, events: pd.DataFrame) -> dict:
    a, b = _prep(old), _prep(new)
    common = sorted(set(a.index) & set(b.index))
    old_priced = sum(_num(a.loc[i].get('price')) is not None for i in common)
    new_priced = sum(_num(b.loc[i].get('price')) is not None for i in common)
    counts = events['event_type'].value_counts().to_dict() if len(events) else {}
    return {
        'comparable_variants': int(len(common)),
        'old_priced_comparable': int(old_priced),
        'new_priced_comparable': int(new_priced),
        'commercial_events_total': int(len(events)),
        'price_increased': int(counts.get('PRICE_INCREASED', 0)),
        'price_decreased': int(counts.get('PRICE_DECREASED', 0)),
        'markdown_started': int(counts.get('MARKDOWN_STARTED', 0)),
        'markdown_ended': int(counts.get('MARKDOWN_ENDED', 0)),
        'markdown_deepened': int(counts.get('MARKDOWN_DEEPENED', 0)),
        'markdown_reduced': int(counts.get('MARKDOWN_REDUCED', 0)),
        'entered_sale': int(counts.get('ENTERED_SALE', 0)),
        'left_sale': int(counts.get('LEFT_SALE', 0)),
    }


def enriched_snapshots(path='data/snapshots'):
    return sorted(Path(path).glob('snapshot_*_enriched.csv'))


def compare_latest_enriched_snapshots(snapshot_dir: Path, output_dir: Path):
    files = enriched_snapshots(snapshot_dir)
    if len(files) < 2:
        raise FileNotFoundError('São necessários pelo menos dois snapshots *_enriched.csv.')
    old_path, new_path = files[-2], files[-1]
    old, new = pd.read_csv(old_path), pd.read_csv(new_path)
    events = compare_commercial_snapshots(old, new)
    kpis = commercial_temporal_kpis(old, new, events)
    kpis['old_snapshot'] = old_path.name
    kpis['new_snapshot'] = new_path.name

    output_dir.mkdir(parents=True, exist_ok=True)
    events.to_csv(output_dir / 'commercial_temporal_events.csv', index=False)
    (output_dir / 'commercial_temporal_kpis.json').write_text(
        json.dumps(kpis, ensure_ascii=False, indent=2), encoding='utf-8'
    )

    # Persist a compact comparison ledger for auditability.
    a, b = _prep(old), _prep(new)
    rows = []
    for pid in sorted(set(a.index) & set(b.index)):
        x, y = a.loc[pid], b.loc[pid]
        op, np = _num(x.get('price')), _num(y.get('price'))
        od, nd = _discount(x), _discount(y)
        rows.append({
            'product_id': pid, 'name': y.get('name'), 'category': y.get('category'), 'color': y.get('color'),
            'old_price': op, 'new_price': np,
            'old_discount_pct': od, 'new_discount_pct': nd,
            'old_in_sale': _sale_state(x), 'new_in_sale': _sale_state(y),
            'price_changed': not _same(op, np),
            'markdown_changed': not _same(od, nd, tol=0.01),
        })
    pd.DataFrame(rows).to_csv(output_dir / 'commercial_temporal_comparison.csv', index=False)
    return old_path, new_path, events, kpis
