

---

## 13. Continuous Re-optimization

- Background worker (`services/optimization/reopt_worker.py`) listens to `/stream/events` and re-runs the CVXPY solver on triggers (ingestion, simulation, hazards, alerts, IoT, shocks).
- Env: `REOPT_ENABLED=true` (default).
- Uses in-memory `STATE` to read latest risk buckets populated by `/ingest/exposure`.

## 14. Expanded CEDE/OED Mappings

- `services/ingestion/schema_registry.py` now includes broader CEDE/OED field variants.
- Heuristics derive `tiv` (sum of components) and `pml` from `PML%` × `tiv` when needed.
