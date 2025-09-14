from __future__ import annotations
import os, asyncio, time
from typing import Dict, Any
from sqlalchemy.orm import Session
from database import SessionLocal
from services.streaming.broker import EVENT_BUS
from services.optimization.optimizer import optimize_cvx
from services.state.store import STATE
from services.state.db_risks import get_latest_risks
from services.decisions.store import record_event
TRIGGERS = {"INGESTION_COMPLETE","SIMULATION_COMPLETE","HAZARD_UPLOAD","ALERTS_EVALUATED","IOT_EVENT","VENDOR_FETCH","SHOCK_TOGGLE"}
def should_trigger(ev: Dict[str, Any]) -> bool:
    t = ev.get("type")
    if t in TRIGGERS: return True
    if t == "ALERTS_EVALUATED" and (ev.get("alerts") or []): return True
    return bool(ev.get("breach") is True)
async def reoptimize_once(ev: Dict[str, Any]):
    row = get_latest_risks(SessionLocal()); risks = row[0] if row else STATE.get_risks()
    if not risks: return
    d = STATE.get_defaults()
    out = optimize_cvx(risks, d.get("capital_limit", 1e6), d.get("tvar_cap", 5e6), d.get("lambda_cost", 0.05), d.get("min_alloc", 0.0), d.get("max_alloc", 0.6))
    out["risks"] = risks; out["reason"] = {"trigger_event": ev.get("type")}
    db: Session = SessionLocal()
    try: record_event(db, "REOPTIMIZATION_DECISION", out)
    finally: db.close()
    await EVENT_BUS.publish({"type":"REOPTIMIZATION_DECISION", **out, "ts": int(time.time())})
async def start_reopt_loop():
    if os.getenv("REOPT_ENABLED","true").lower() not in ("1","true","yes"): return
    async for ev in EVENT_BUS.stream():
        try:
            if should_trigger(ev): await reoptimize_once(ev)
        except Exception as e:
            await EVENT_BUS.publish({"type":"REOPT_ERROR","error": str(e)})
