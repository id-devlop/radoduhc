
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Layer:
    attachment: float
    limit: float

def apply_xol_layers(gross_losses: np.ndarray, layers: List[Layer]) -> Dict[str, np.ndarray]:
    """Apply a stack of XoL layers sequentially and return dict of net per layer and portfolio net."""
    layer_nets = {}
    remaining = gross_losses.copy()
    for i, L in enumerate(layers):
        # loss above attachment up to attachment+limit
        covered = np.clip(remaining - L.attachment, 0, L.limit)
        layer_nets[f"L{i+1}"] = covered
        # remaining keeps being the same gross (we're reporting layer ceded); portfolio net after all layers:
    # portfolio net = gross - sum(covered)
    total_covered = sum(layer_nets[k] for k in layer_nets)
    portfolio_net = gross_losses - total_covered
    layer_nets["PORTFOLIO_NET"] = portfolio_net
    return layer_nets

def simulate_mc(trials:int=100000, lam:float=0.5, sev_mean:float=14.0, sev_sd:float=1.2, tiv:float=1e9, layers_cfg:List[Dict[str,float]] = None, seed:int=42) -> Dict[str, Any]:
    """
    Frequency: Poisson(lam) events per year
    Severity: lognormal on loss size (in currency), derived from mean/sd in log-space, scaled to a fraction of TIV if needed.
    For simplicity, we simulate *annual* loss as sum of event severities, then apply XoL on the annual loss (annual agg XoL-style).
    """
    rng = np.random.default_rng(seed)
    N = int(trials)
    # sample frequencies
    freq = rng.poisson(lam=lam, size=N)
    # sample severities for each trial as sum of lognormal draws
    # Draw maximum of, say, 20 events; for zero, loss=0
    max_events = max(1, min(50, int(lam*10)+10))
    sev_draws = rng.lognormal(mean=sev_mean, sigma=sev_sd, size=(N, max_events))
    # Mask to keep only freq events per row
    mask = np.arange(max_events)[None, :] < freq[:, None]
    annual_gross = (sev_draws * mask).sum(axis=1)
    # If sev params are intended as loss ratio, allow tiv scaling via small means; keep tiv hook
    if tiv and tiv > 0 and annual_gross.mean() < 1.0:
        annual_gross = annual_gross * tiv
    # Layers
    layers = [Layer(**d) for d in (layers_cfg or [])]
    if layers:
        nets = apply_xol_layers(annual_gross, layers)
        portfolio_net = nets["PORTFOLIO_NET"]
    else:
        portfolio_net = annual_gross
        nets = {"PORTFOLIO_NET": portfolio_net}
    # Metrics
    def var_tvar(arr, q=0.99):
        v = np.quantile(arr, q)
        t = arr[arr>=v].mean() if (arr>=v).any() else float(v)
        return float(v), float(t)
    v99, tv99 = var_tvar(portfolio_net, 0.99)
    out = {
        "trials": N,
        "freq_mean": float(freq.mean()),
        "gross_mean": float(annual_gross.mean()),
        "net_mean": float(portfolio_net.mean()),
        "var99": v99,
        "tvar99": tv99,
        "layers": {k: {"mean": float(v.mean())} for k,v in nets.items()},
    }
    return out
