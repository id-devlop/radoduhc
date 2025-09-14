
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from services.mc_engine.simulate_mc_adv import simulate_mc_adv

router = APIRouter()

class TreatyIn(BaseModel):
    type: str = Field(..., pattern="^(AGG_XOL|STOP_LOSS)$")
    attachment: float = Field(0, ge=0)
    limit: float = Field(..., ge=0)
    reinstatements: int = Field(0, ge=0, le=6)

class SimulateIn(BaseModel):
    trials: int = Field(200000, ge=1000, le=5000000)
    tiv: float = 1e9
    lam: float = Field(0.6, ge=0.0, le=50.0)
    sev_mean: float = 14.0
    sev_sd: float = 1.2
    treaties: List[TreatyIn] = []
    corr_matrix: Optional[List[List[float]]] = None
    copula: str = Field("independent", description="independent | t-copula")
    df: float = 5.0
    seed: int = 42

@router.post("/run")
def run(req: SimulateIn) -> Dict[str, Any]:
    res = simulate_mc_adv(trials=req.trials, tiv=req.tiv, lam=req.lam, sev_mean=req.sev_mean, sev_sd=req.sev_sd,
                          treaties_cfg=[t.model_dump() for t in req.treaties], corr_matrix=req.corr_matrix,
                          copula=req.copula, df=req.df, seed=req.seed)
    return res
