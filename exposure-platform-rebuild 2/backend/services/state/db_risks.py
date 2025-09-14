from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import Table, Column, Integer, String, DateTime, JSON, MetaData, func, select, insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from database import engine as _engine

_metadata = MetaData()

risk_snapshots = Table(
    "risk_snapshots",
    _metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("label", String(255), nullable=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("params", JSON, nullable=True),
    Column("risks", JSON, nullable=False),
)

def create_tables(engine: Engine | None = None) -> None:
    engine = engine or _engine
    _metadata.create_all(bind=engine, tables=[risk_snapshots])

def save_risks(db: Session, risks: List[Dict[str, Any]], params: Dict[str, Any] | None = None, label: Optional[str] = None) -> int:
    create_tables()
    ins = insert(risk_snapshots).values(label=label, params=params or {}, risks=risks).returning(risk_snapshots.c.id)
    rid = db.execute(ins).scalar_one()
    db.commit()
    return int(rid)

def get_latest_risks(db: Session) -> Optional[Tuple[List[Dict[str, Any]], Dict[str, Any]]]:
    create_tables()
    stmt = select(risk_snapshots.c.risks, risk_snapshots.c.params).order_by(risk_snapshots.c.id.desc()).limit(1)
    row = db.execute(stmt).first()
    if not row:
        return None
    risks, params = row[0], row[1] or {}
    return risks, params

def list_snapshots(db: Session, limit: int = 50) -> List[Dict[str, Any]]:
    create_tables()
    stmt = select(risk_snapshots.c.id, risk_snapshots.c.label, risk_snapshots.c.created_at).order_by(risk_snapshots.c.id.desc()).limit(limit)
    return [{"id": r.id, "label": r.label, "created_at": str(r.created_at)} for r in db.execute(stmt).fetchall()]
