
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import os, json

router = APIRouter()

MODEL_PATH = os.getenv("VULN_MODEL_PATH", "models/vuln_model.pkl")

class TrainIn(BaseModel):
    features: List[Dict[str, float]]
    targets: List[float]

class ExplainIn(BaseModel):
    features: Dict[str, float]
    im: float = Field(0, description="Intensity measure (e.g., flood depth m, wind gust m/s, etc.)")
    baseline: float = 0.0

@router.post("/train")
def train(req: TrainIn) -> Dict[str, Any]:
    """Train a simple gradient boosting model and save it; fallback to linear if libs missing."""
    try:
        import numpy as np
        from sklearn.ensemble import GradientBoostingRegressor
        import joblib
        X = np.array([[d.get(k,0.0) for k in sorted(req.features[0].keys())] for d in req.features])
        y = np.array(req.targets)
        mdl = GradientBoostingRegressor(random_state=42).fit(X, y)
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        meta = {"feature_order": sorted(req.features[0].keys())}
        joblib.dump({"model": mdl, "meta": meta}, MODEL_PATH)
        return {"status":"ok", "path": MODEL_PATH}
    except Exception as e:
        return {"status":"error", "error": str(e)}

@router.post("/delta")
def delta(req: ExplainIn) -> Dict[str, Any]:
    # Try SHAP explanation on stored model; fall back to weighted linear scheme.
    try:
        import numpy as np, joblib, shap
        bundle = joblib.load(MODEL_PATH)
        mdl, meta = bundle["model"], bundle["meta"]
        order = meta["feature_order"]
        x = np.array([[req.features.get(k,0.0) for k in order]])
        explainer = shap.Explainer(mdl)
        sv = explainer(x).values[0].tolist()
        contributions = [{"feature": k, "delta": float(v)} for k,v in zip(order, sv)]
        total = float(mdl.predict(x)[0]) + 0.01 * req.im + req.baseline
        return {"DeltaRisk": max(0.0, total), "contributions": contributions, "method": "SHAP"}
    except Exception:
        weights = {
            "roof_class_A": -0.06,
            "defensible_space": -0.04,
            "elevation": -0.03,
            "drainage_index": -0.05,
            "construction_wood": 0.07,
            "wui": 0.06,
            "age": 0.02,
        }
        contribs: List[Dict[str, Any]] = []
        total = req.baseline + 0.01 * req.im
        for k,v in req.features.items():
            w = weights.get(k, 0.01)
            c = float(w * v)
            contribs.append({"feature": k, "weight": w, "value": v, "delta": c})
            total += c
        return {"DeltaRisk": max(0.0, total), "contributions": contribs, "method": "linear"}
