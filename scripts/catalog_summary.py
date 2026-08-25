from pathlib import Path
import pandas as pd

p = Path(__file__).resolve().parents[1] / "data" / "processed" / "inti_catalog_latest.csv"
df = pd.read_csv(p)
print("INTI Catalog Summary")
print("="*40)
print("Produtos:", len(df))
print("Coleções:")
print(df["collection"].fillna("N/D").value_counts().to_string())
print("\nCategorias:")
print(df["category"].fillna("N/D").value_counts().to_string())
print("\nCores:")
print(df["color"].fillna("N/D").value_counts().head(20).to_string())
print("\nCom desconto:", int(df["discount_pct"].fillna(0).gt(0).sum()))
print("Com sinal de indisponibilidade:", int(df["availability_text"].astype(str).str.contains("unavailable", case=False).sum()))
