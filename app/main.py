from fastapi import FastAPI
from app.api.intelligence import router as intelligence_router

app = FastAPI(
    title="INTI Intelligence API",
    version="0.1.0",
    description="Demand & Inventory Intelligence for premium fashion."
)
app.include_router(intelligence_router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok", "product": "INTI Intelligence", "version": "0.1.0"}
