from __future__ import annotations
from typing import Any, List, Dict, Optional
import threading
class _StateStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._risks: Optional[List[Dict[str, Any]]] = None
        self._defaults = {"capital_limit": 1_000_000.0, "tvar_cap": 5_000_000.0, "lambda_cost": 0.05, "min_alloc": 0.0, "max_alloc": 0.6}
    def set_risks(self, risks: List[Dict[str, Any]]):
        with self._lock: self._risks = risks
    def get_risks(self) -> Optional[List[Dict[str, Any]]]:
        with self._lock: return self._risks
    def set_defaults(self, **kwargs):
        with self._lock: self._defaults.update(kwargs)
    def get_defaults(self) -> Dict[str, float]:
        with self._lock: return dict(self._defaults)
STATE = _StateStore()
