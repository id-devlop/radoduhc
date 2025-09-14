
from fastapi import APIRouter

router = APIRouter()

@router.get("/ingest")
def ingest():
    # placeholder endpoint
    return {"status":"ok","features_ingested": 0}
