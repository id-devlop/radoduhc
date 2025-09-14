
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from database import get_db
from models import AuditEvent
from schemas import AuditEventIn
import csv, io, json

router = APIRouter()

@router.post("/event")
def write_event(ev: AuditEventIn, db: Session = Depends(get_db)):
    row = AuditEvent(type=ev.type, user_name=ev.user, user_role=ev.role, payload=ev.data or {})
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id}

@router.get("/history")
def history(limit: int = 100, format: str = "json", db: Session = Depends(get_db)):
    q = db.query(AuditEvent).order_by(AuditEvent.id.desc()).limit(limit).all()
    if format == "csv":
        output = io.StringIO()
        w = csv.writer(output)
        w.writerow(["id","type","user_name","user_role","timestamp","payload"])
        for r in q:
            w.writerow([r.id,r.type,r.user_name,r.user_role,r.timestamp,r.payload])
        return Response(content=output.getvalue(), media_type="text/csv")
    return {"events": [{
        "id": r.id, "type": r.type, "user": r.user_name, "role": r.user_role,
        "timestamp": r.timestamp.isoformat(), "payload": r.payload
    } for r in q]}
