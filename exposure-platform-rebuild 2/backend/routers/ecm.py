
from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()

@router.post("/push")
def push_to_ecm(payload: Dict[str, Any]):
    # Accept JSON blob and pretend to hand off to ECM
    return {"status":"queued","items": len(payload.get("positions", []))}

@router.get("/pull")
def pull_from_ecm():
    # toy response
    return {"capital_curve":[{"rp":10,"capital":100},{"rp":100,"capital":300},{"rp":250,"capital":550}]}
