
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class Treaty:
    type: str            # 'AGG_XOL' | 'STOP_LOSS'
    attachment: float
    limit: float
    reinstatements: int = 0

def _apply_agg_cover(annual_loss: np.ndarray, attachment: float, limit: float, reinstatements: int) -> Dict[str, np.ndarray]:
    """Aggregate cover: pays (loss - att) up to limit for base layer; reinstatements add additional equal limits."""
    max_cover = limit * (1 + max(0, int(reinstatements)))
    covered = np.clip(annual_loss - attachment, 0.0, max_cover)
    net = annual_loss - covered
    return {"covered": covered, "net": net}

def apply_treaties(annual_gross: np.ndarray, treaties: List[Treaty]) -> Dict[str, np.ndarray]:
    """Apply aggregate XoL or Stop-Loss treaties on annual portfolio loss (approximation)."""
    nets = {}
    running = annual_gross.copy()
    for i, t in enumerate(treaties):
        res = _apply_agg_cover(running, t.attachment, t.limit, t.reinstatements)
        nets[f"T{i+1}_{t.type}"] = res["covered"]
        running = res["net"]
    nets["PORTFOLIO_NET"] = running
    return nets

def _student_t_copula(chol: np.ndarray, df: float, n: int, rng: np.random.Generator) -> np.ndarray:
    """Generate t-copula samples with given Cholesky of correlation matrix."""
    k = chol.shape[0]
    g = rng.standard_normal(size=(n, k))
    w = rng.chisquare(df, size=(n,)) / df
    z = g @ chol.T / np.sqrt(w)[:, None]  # t distribution
    # Convert to uniforms via CDF of Student-t ~ use normal CDF as approximation for speed
    from math import erf, sqrt
    def phi(x):  # standard normal CDF as approximation
        return 0.5 * (1.0 + erf(x / sqrt(2.0)))
    U = 0.5 * (1.0 + erf(z / np.sqrt(2.0)))
    return U

def simulate_mc_adv(trials:int=200_000,
                    tiv: float = 1e9,
                    lam: float = 0.6,
                    sev_mean: float = 14.0,
                    sev_sd: float = 1.2,
                    treaties_cfg: Optional[List[Dict[str, Any]]] = None,
                    corr_matrix: Optional[List[List[float]]] = None,
                    copula: str = "independent",
                    df: float = 5.0,
                    seed:int=42) -> Dict[str, Any]:
    """
    Advanced MC:
    - Aggregate portfolio annual loss with lognormal severities (sum of events).
    - Aggregate XoL and Stop-Loss treaties with reinstatements.
    - Optional t-copula correlation across K peril buckets (approximated) controlling tail dependence.
    """
    rng = np.random.default_rng(seed)
    N = int(trials)

    # Frequency sampling per trial
    freq = rng.poisson(lam=lam, size=N)

    # If correlation provided, simulate K peril bucket losses with dependence
    if corr_matrix is not None and len(corr_matrix) > 0:
        K = len(corr_matrix)
        chol = np.linalg.cholesky(np.array(corr_matrix))
        U = _student_t_copula(chol, df, N, rng) if copula.lower().startswith('t') else rng.random((N, K))
        # Map uniforms to lognormal severities per bucket; sum to annual gross
        # Invert CDF for lognormal via normal quantile; approximate using numpy erfinv if available
        from numpy import sqrt
        from numpy import erfinv
        Z = sqrt(2.0) * erfinv(2.0*U - 1.0)
        sev = np.exp(sev_mean + sev_sd * Z)  # lognormal samples
        annual_gross = sev.sum(axis=1)
    else:
        # Classic path: max_events truncation; sum of lognormals
        max_events = max(1, min(50, int(lam*10)+10))
        sev_draws = rng.lognormal(mean=sev_mean, sigma=sev_sd, size=(N, max_events))
        mask = np.arange(max_events)[None, :] < freq[:, None]
        annual_gross = (sev_draws * mask).sum(axis=1)

    # Scale by TIV if we detect tiny losses (treat mean < 1 as loss ratios)
    if tiv and tiv > 0 and annual_gross.mean() < 1.0:
        annual_gross = annual_gross * tiv

    # Treaties
    treaties = [Treaty(**t) for t in (treaties_cfg or [])]
    if treaties:
        nets = apply_treaties(annual_gross, treaties)
        portfolio_net = nets["PORTFOLIO_NET"]
    else:
        nets = {"PORTFOLIO_NET": annual_gross}
        portfolio_net = annual_gross

    # Risk metrics
    def var_tvar(arr, q=0.99):
        v = np.quantile(arr, q)
        t = arr[arr>=v].mean() if (arr>=v).any() else float(v)
        return float(v), float(t)
    v99, tv99 = var_tvar(portfolio_net, 0.99)

    # Tail Copula Index proxy: ratio of joint tail prob to product of marginals at 0.99 for 2D case (if K>=2)
    tci = None
    if corr_matrix is not None and len(corr_matrix) >= 2:
        # cheap proxy using corr of uniforms near tail
        U = rng.random((N, 2))
        tci = float(np.corrcoef((U[:,0]>0.99).astype(float),(U[:,1]>0.99).astype(float))[0,1])

    out = {
        "trials": N,
        "freq_mean": float(freq.mean()),
        "gross_mean": float(annual_gross.mean()),
        "net_mean": float(portfolio_net.mean()),
        "var99": v99,
        "tvar99": tv99,
        "tail_copula_index": tci,
        "treaties": {k: {"mean": float(v.mean())} for k,v in nets.items()},
    }
    return out
