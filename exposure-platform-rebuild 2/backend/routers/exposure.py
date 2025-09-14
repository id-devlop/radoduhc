
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Exposure
from schemas import ExposureIn
from typing import List, Dict, Any
from sqlalchemy import text

router = APIRouter()

@router.post("")
def upsert_exposure(e: ExposureIn, db: Session = Depends(get_db)):
    row = Exposure(**e.model_dump())
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id}

@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    # Simple aggregate by LoB and jurisdiction
    rows = db.execute(text("""
        SELECT lob, jurisdiction, count(*) as cnt,
               sum( (metrics->>'tsi')::numeric ) as tsi,
               sum( (metrics->>'aal')::numeric ) as aal,
               sum( (metrics->>'pml')::numeric ) as pml
        FROM exposures
        GROUP BY lob, jurisdiction
        ORDER BY lob, jurisdiction
    """)).fetchall()
    return {"summary":[dict(r._mapping) for r in rows]}

@router.get("/by-geo")
def by_geo(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT id, lob, subclass, jurisdiction, geography, metrics
        FROM exposures ORDER BY id DESC LIMIT 500
    """)).fetchall()
    features = []
    for r in rows:
        g = r._mapping['geography'] or {}
        coords = g.get('coordinates') or g.get('coord') or [0,0]
        features.append({
            "type":"Feature",
            "geometry":{"type":"Point","coordinates":coords},
            "properties":{
                "id": r._mapping['id'], "lob": r._mapping['lob'], "jurisdiction": r._mapping['jurisdiction'],
                "tsi": (r._mapping['metrics'] or {}).get('tsi')
            }
        })
    return {"type":"FeatureCollection","features":features}
