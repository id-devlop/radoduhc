from __future__ import annotations
from typing import List, Dict, Any
import numpy as np

def optimize_cvx(risks: List[Dict[str, Any]],
                 capital_limit: float,
                 tvar_cap: float,
                 lambda_cost: float = 0.05,
                 min_alloc: float = 0.0,
                 max_alloc: float = 0.6) -> Dict[str, Any]:
    import cvxpy as cp
    n = len(risks)
    if n == 0:
        return {"weights": [], "objective": 0.0, "status": "EMPTY"}
    mean_losses = np.array([float(r.get("mean_loss", 0.0)) for r in risks], dtype=float)
    tvars = np.array([float(r.get("tvar99", mean_losses[i]*3.0)) for i,r in enumerate(risks)], dtype=float)
    rols = np.array([float(r.get("rol", 0.0)) for r in risks], dtype=float)
    x = cp.Variable(n)
    constraints = [x >= min_alloc, x <= max_alloc, cp.sum(x) <= 1.0,
                   mean_losses @ x <= capital_limit, tvars @ x <= tvar_cap]
    objective = cp.Minimize(mean_losses @ x + lambda_cost * cp.norm1(rols * x))
    prob = cp.Problem(objective, constraints)
    prob.solve(solver=cp.ECOS, warm_start=True)
    return {
        "status": prob.status,
        "objective": float(prob.value) if prob.value is not None else None,
        "weights": x.value.tolist() if x.value is not None else [0.0]*n,
        "expected_loss": float((mean_losses @ x.value)) if x.value is not None else None,
        "tvar": float((tvars @ x.value)) if x.value is not None else None
    }

def _derive_premiums(risks: List[Dict[str, Any]], mean_losses: np.ndarray, rols: np.ndarray, premium_factor: float) -> np.ndarray:
    prem = []
    for i, r in enumerate(risks):
        if r.get("premium") is not None:
            prem.append(float(r["premium"]))
        elif r.get("est_premium") is not None:
            prem.append(float(r["est_premium"])) 
        else:
            prem.append(float(premium_factor) * float(rols[i]) * float(mean_losses[i]))
    return np.array(prem, dtype=float)

def optimize_cvx_multi(risks: List[Dict[str, Any]],
                       capital_limit: float,
                       tvar_cap: float,
                       lambda_cost: float = 0.05,
                       min_alloc: float = 0.0,
                       max_alloc: float = 0.6,
                       strategy: str = "scalar",
                       w_mean: float = 1.0,
                       w_tvar: float = 0.0,
                       w_premium: float = 0.0,
                       premium_factor: float = 0.25,
                       tvar_epsilon: float | None = None,
                       premium_epsilon: float | None = None) -> Dict[str, Any]:
    import cvxpy as cp
    n = len(risks)
    if n == 0:
        return {"weights": [], "objective": 0.0, "status": "EMPTY"}
    mean_losses = np.array([float(r.get("mean_loss", 0.0)) for r in risks], dtype=float)
    tvars = np.array([float(r.get("tvar99", mean_losses[i]*3.0)) for i,r in enumerate(risks)], dtype=float)
    rols = np.array([float(r.get("rol", 0.0)) for r in risks], dtype=float)
    premiums = _derive_premiums(risks, mean_losses, rols, premium_factor)
    x = cp.Variable(n)
    constraints = [x >= min_alloc, x <= max_alloc, cp.sum(x) <= 1.0,
                   mean_losses @ x <= capital_limit, tvars @ x <= tvar_cap]
    if strategy.lower() == "epsilon":
        if tvar_epsilon is not None:
            constraints.append(tvars @ x <= tvar_epsilon)
        if premium_epsilon is not None:
            constraints.append(premiums @ x <= premium_epsilon)
        objective = cp.Minimize(mean_losses @ x + lambda_cost * cp.norm1(rols * x))
    else:
        objective = cp.Minimize(w_mean * (mean_losses @ x) + w_tvar * (tvars @ x) + w_premium * (premiums @ x) + lambda_cost * cp.norm1(rols * x))
    prob = cp.Problem(objective, constraints)
    prob.solve(solver=cp.ECOS, warm_start=True)
    return {
        "status": prob.status,
        "objective": float(prob.value) if prob.value is not None else None,
        "weights": x.value.tolist() if x.value is not None else [0.0]*n,
        "expected_loss": float((mean_losses @ x.value)) if x.value is not None else None,
        "tvar": float((tvars @ x.value)) if x.value is not None else None,
        "premium": float((premiums @ x.value)) if x.value is not None else None,
        "objective_terms": {"w_mean": w_mean, "w_tvar": w_tvar, "w_premium": w_premium, "lambda_cost": lambda_cost}
    }
