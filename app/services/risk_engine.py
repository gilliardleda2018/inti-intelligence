from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

DATA = Path(__file__).resolve().parents[2] / "data" / "sku_weekly.csv"
DATA_SYNTHETIC = Path(__file__).resolve().parents[2] / "data" / "synthetic" / "sku_weekly.csv"

def load_and_score():
    path = DATA if DATA.exists() else DATA_SYNTHETIC
    if not path.exists():
        return []
        
    df = pd.read_csv(path)
    if df.empty:
        return []
        
    # Build lag features for time series forecasting
    df_sorted = df.sort_values(["sku", "week"]).copy()
    df_sorted["lag_1"] = df_sorted.groupby("sku")["units_sold"].shift(1)
    df_sorted["lag_2"] = df_sorted.groupby("sku")["units_sold"].shift(2)
    df_sorted["lag_3"] = df_sorted.groupby("sku")["units_sold"].shift(3)
    df_sorted["lag_4"] = df_sorted.groupby("sku")["units_sold"].shift(4)
    
    # Train forecasting model using lags (RandomForestRegressor)
    train_df = df_sorted.dropna(subset=["lag_1", "lag_2", "lag_3", "lag_4"])
    if not train_df.empty:
        X = train_df[["lag_1", "lag_2", "lag_3", "lag_4"]]
        y = train_df["units_sold"]
        model = RandomForestRegressor(n_estimators=30, random_state=42)
        model.fit(X, y)
        has_model = True
    else:
        has_model = False

    # Get recent history per SKU
    recent = (
        df.sort_values("week")
          .groupby(["sku","product","color","size"], as_index=False)
          .tail(8)
    )
    
    agg = recent.groupby(
        ["sku","product","color","size"], as_index=False
    ).agg(
        avg_weekly_demand=("units_sold","mean"),
        current_stock=("ending_stock","last"),
        price=("price","last")
    )
    
    # Generate 4 weeks forecast using recursive lags if model is available,
    # otherwise fallback to simple mean * 4
    forecasts = []
    for _, row in agg.iterrows():
        sku = row["sku"]
        if has_model:
            # get last 4 observed weeks for this SKU
            sku_history = df_sorted[df_sorted["sku"] == sku].tail(4)
            history = list(sku_history["units_sold"])
            if len(history) < 4:
                history = [row["avg_weekly_demand"]] * 4
            
            curr_lags = list(history)
            sku_forecast = []
            for _ in range(4):
                pred_df = pd.DataFrame([curr_lags[-4:]], columns=["lag_1", "lag_2", "lag_3", "lag_4"])
                pred = model.predict(pred_df)[0]
                sku_forecast.append(pred)
                curr_lags.append(pred)
            forecasts.append(sum(sku_forecast))
        else:
            forecasts.append(row["avg_weekly_demand"] * 4)
            
    agg["forecast_4w"] = [round(f, 1) for f in forecasts]
    
    agg["weeks_cover"] = (
        agg["current_stock"] / agg["avg_weekly_demand"].replace(0, 0.1)
    ).round(1)
    
    agg["stockout_risk"] = (
        (agg["weeks_cover"] < 2.0).astype(float) * 0.95 +
        ((agg["weeks_cover"] >= 2.0) & (agg["weeks_cover"] < 4.0)).astype(float) * 0.65 +
        (agg["weeks_cover"] >= 4.0).astype(float) * 0.15
    )
    
    agg["overstock_risk"] = (
        (agg["weeks_cover"] > 10).astype(float) * 0.90 +
        ((agg["weeks_cover"] > 6) & (agg["weeks_cover"] <= 10)).astype(float) * 0.60 +
        (agg["weeks_cover"] <= 6).astype(float) * 0.10
    )
    
    agg["revenue_at_risk"] = (
        (agg["forecast_4w"] - agg["current_stock"]).clip(lower=0) * agg["price"]
    ).round(2)
    
    agg = agg.sort_values(["revenue_at_risk","stockout_risk"], ascending=False)
    return agg.round(3).to_dict(orient="records")
