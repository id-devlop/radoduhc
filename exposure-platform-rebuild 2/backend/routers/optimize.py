from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database import get_db
from services.decisions.store import record_event
from services.optimization.optimizer import optimize_cvx_multi
from services.streaming.broker import EVENT_BUS
import time

router = APIRouter()

class RiskItem(BaseModel):
    name: Optional[str] = None
    mean_loss: float = Field(..., ge=0.0)
    tvar99: Optional[float] = Field(0.0, ge=0.0)
    rol: Optional[float] = Field(0.0, ge=0.0)
    premium: Optional[float] = Field(None, ge=0.0)

class OptimizeIn(BaseModel):
    risks: List[RiskItem]
    capital_limit: float = Field(..., ge=0.0)
    tvar_cap: float = Field(..., ge=0.0)
    strategy: str = Field("scalar", pattern="^(scalar|epsilon)$")
    w_mean: float = Field(1.0, ge=0.0)
    w_tvar: float = Field(0.0, ge=0.0)
    w_premium: float = Field(0.0, ge=0.0)
    premium_factor: float = Field(0.25, ge=0.0)
    tvar_epsilon: Optional[float] = Field(None, ge=0.0)
    premium_epsilon: Optional[float] = Field(None, ge=0.0)
    lambda_cost: float = Field(0.05, ge=0.0)
    min_alloc: float = Field(0.0, ge=0.0)
    max_alloc: float = Field(0.6, ge=0.0)

@router.post("/capital")
async def optimize_capital(inp: OptimizeIn, db: Session = Depends(get_db)) -> Dict[str, Any]:
    risks = [r.model_dump() for r in inp.risks]
    out = optimize_cvx_multi(
        risks=risks,
        capital_limit=inp.capital_limit,
        tvar_cap=inp.tvar_cap,
        lambda_cost=inp.lambda_cost,
        min_alloc=inp.min_alloc,
        max_alloc=inp.max_alloc,
        strategy=inp.strategy,
        w_mean=inp.w_mean,
        w_tvar=inp.w_tvar,
        w_premium=inp.w_premium,
        premium_factor=inp.premium_factor,
        tvar_epsilon=inp.tvar_epsilon,
        premium_epsilon=inp.premium_epsilon,
    )
    out["risks"] = risks
    record_event(db, "OPTIMIZATION_DECISION", out)
    await EVENT_BUS.publish({"type":"OPTIMIZATION_DECISION", **out, "ts": int(time.time())})
    return out
