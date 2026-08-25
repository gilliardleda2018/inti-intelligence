from pathlib import Path
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
out = Path(__file__).resolve().parents[1] / "data" / "sku_weekly.csv"

products = [
    ("VEST-SALVI","Vestido Salvi",1499.0),
    ("VEST-FONT","Vestido Fontaine",1699.0),
    ("VEST-WILL","Vestido Willow",1449.0),
    ("BLAZ-ARIA","Blazer Aria",1299.0),
    ("CALC-LUME","Calça Lume",899.0),
]
colors = ["Preto","Vermelho","Off White","Azul"]
sizes = [34,36,38,40,42,44]
weeks = pd.date_range("2025-09-01", periods=52, freq="W-MON")

rows = []
for code, product, price in products:
    for color in colors:
        for size in sizes:
            base = rng.uniform(0.8, 6.0)
            if size in (36,38,40): base *= 1.5
            if color in ("Preto","Vermelho"): base *= 1.25
            stock = int(rng.integers(18, 65))
            for i, week in enumerate(weeks):
                season = 1 + 0.35*np.sin((i/52)*2*np.pi)
                sold = int(max(0, rng.poisson(base*season)))
                stock = max(0, stock - sold)
                if stock < 8 and rng.random() < 0.35:
                    stock += int(rng.integers(12, 35))
                rows.append({
                    "week": week.date().isoformat(),
                    "sku": f"{code}-{color[:3].upper()}-{size}",
                    "product": product,
                    "color": color,
                    "size": size,
                    "price": price,
                    "units_sold": sold,
                    "ending_stock": stock
                })

pd.DataFrame(rows).to_csv(out, index=False)
print(f"Generated {len(rows)} rows -> {out}")
