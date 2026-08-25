from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from inti_intelligence.commercial_temporal import compare_latest_enriched_snapshots

old_path, new_path, events, kpis = compare_latest_enriched_snapshots(
    ROOT / 'data' / 'snapshots', ROOT / 'data' / 'output'
)

print('INTI Commercial Temporal Intelligence')
print('-------------------------------------')
print(f'{old_path.name} -> {new_path.name}')
for key in [
    'comparable_variants', 'commercial_events_total',
    'price_increased', 'price_decreased',
    'markdown_started', 'markdown_ended',
    'markdown_deepened', 'markdown_reduced',
    'entered_sale', 'left_sale',
]:
    print(f'{key}: {kpis[key]}')
print(f"Output: {ROOT / 'data' / 'output' / 'commercial_temporal_events.csv'}")
