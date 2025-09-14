
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Binding
from pydantic import BaseModel

router = APIRouter()

class BindIn(BaseModel):
    audit_id: str
    user: str | None = None

@router.post("")
def bind(inb: BindIn, db: Session = Depends(get_db)):
    row = Binding(audit_id=inb.audit_id, bound_by=inb.user or "cuo")
    db.add(row); db.commit(); db.refresh(row)
    return {"binding_id": f"BIND-{row.id}"}
