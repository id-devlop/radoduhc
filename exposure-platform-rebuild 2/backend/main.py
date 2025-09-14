
import os, time
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, audit, exposure, config, scenario, correlation, ecm, satellite, bind, export, simulate, explain
from database import engine
from database import Base

app = FastAPI(title="Exposure Platform API", version="2025.08-full")

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure metadata is available
@app.get("/health")
def health():
    return {"status": "ok", "ts": int(time.time())}

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(audit.router, prefix="/audit", tags=["audit"])
app.include_router(exposure.router, prefix="/exposure", tags=["exposure"])
app.include_router(config.router, prefix="/config", tags=["config"])
app.include_router(scenario.router, prefix="/scenario", tags=["scenario"])
app.include_router(correlation.router, prefix="/correlation", tags=["correlation"])
app.include_router(ecm.router, prefix="/ecm", tags=["ecm"])
app.include_router(satellite.router, prefix="/satellite", tags=["satellite"])
app.include_router(bind.router, prefix="/bind", tags=["bind"])
app.include_router(export.router, prefix="/export", tags=["export"])

app.include_router(simulate.router, prefix="/simulate", tags=["simulate"])
app.include_router(explain.router, prefix="/explain", tags=["explain"])
from services.optimization.reopt_worker import start_reopt_loop

@app.on_event("startup")
async def _start_reopt():
    import asyncio
    asyncio.create_task(start_reopt_loop())

from routers import optimize

app.include_router(optimize.router, prefix="/optimize", tags=["optimize"])