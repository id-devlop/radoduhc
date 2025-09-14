
from fastapi import APIRouter
from typing import Dict, Any, List
import numpy as np

router = APIRouter()

@router.post("/estimate")
def estimate(payload: Dict[str, Any]):
    # payload: { series: {key: [values...] } }
    series = payload.get("series", {})
    keys = list(series.keys())
    n = len(keys)
    mat = [[1.0]*n for _ in range(n)]
    # simple Pearson correlation
    for i in range(n):
        for j in range(i+1, n):
            x = np.array(series[keys[i]], dtype=float)
            y = np.array(series[keys[j]], dtype=float)
            if len(x) != len(y) or len(x) < 2:
                corr = 0.0
            else:
                corr = float(np.corrcoef(x,y)[0,1])
            mat[i][j] = mat[j][i] = corr
    return {"keys": keys, "correlation": mat}
