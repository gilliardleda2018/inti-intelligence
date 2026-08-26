from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os

# Add project src to PYTHONPATH when running directly
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))

from inti_intelligence.sentiment_analysis import get_reviews_sentiment_data

app = FastAPI(title="INTI Intelligence API", version="0.1.0")

# Allow all origins for simplicity – adjust for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/sentiment")
def sentiment_endpoint():
    """Return sentiment analysis data as JSON list.
    The underlying function returns a pandas DataFrame; we convert it to a list of dicts.
    """
    df = get_reviews_sentiment_data()
    # Convert DataFrame to list of dicts, ensuring NaNs become None
    return df.where(pd.notnull(df), None).to_dict(orient="records")
