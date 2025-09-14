
from fastapi import APIRouter
from typing import List, Dict, Any
import numpy as np

router = APIRouter()

LIB = [
  {"id":"EQ-250", "name":"Earthquake 1-in-250", "lob":["property","energy"], "shock":{"pml_mult":1.2}},
  {"id":"HU-100", "name":"Hurricane 1-in-100", "lob":["property","marine"], "shock":{"aal_mult":1.4}},
  {"id":"CY-TAIL", "name":"Cyber tail shock", "lob":["casualty"], "shock":{"tail_load":0.3}},
]

@router.get("/library")
def library():
    return {"scenarios": LIB}

@router.post("/run")
def run(payload: Dict[str, Any]):
    scen_id = payload.get("id")
    total = payload.get("total", 1_000_000_000)
    # toy impact calc
    impact = 0.0
    if scen_id == "EQ-250": impact = total * 0.08
    elif scen_id == "HU-100": impact = total * 0.06
    elif scen_id == "CY-TAIL": impact = total * 0.03
    return {"scenario": scen_id, "portfolio_loss": impact, "capital_pct": round(100*impact/max(total,1),3)}
