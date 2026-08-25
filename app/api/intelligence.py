from fastapi import APIRouter, Query
from app.services.risk_engine import load_and_score

router = APIRouter(tags=["intelligence"])

@router.get("/inventory-risk")
def inventory_risk(limit: int = Query(20, ge=1, le=500)):
    rows = load_and_score()
    return {"count": min(limit, len(rows)), "items": rows[:limit]}
