from pathlib import Path
import sys,pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from inti_intelligence.temporal import compare_snapshots
snaps=sorted((ROOT/'data'/'snapshots').glob('*.csv'))
if len(snaps)<2:raise SystemExit('São necessários pelo menos 2 snapshots em data/snapshots.')
old,new=snaps[-2],snaps[-1]
events=compare_snapshots(pd.read_csv(old),pd.read_csv(new))
out=ROOT/'data'/'output'/'temporal_events.csv';events.to_csv(out,index=False)
print(f'{old.name} -> {new.name}')
print(f'Eventos: {len(events)}')
print(events.event_type.value_counts().to_string() if len(events) else 'Nenhuma mudança detectada.')
print(f'Output: {out}')
