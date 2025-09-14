
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, JSON, BigInteger, TIMESTAMP, text
from database import Base

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String)
    user_name: Mapped[str | None] = mapped_column(String, nullable=True)
    user_role: Mapped[str | None] = mapped_column(String, nullable=True)
    timestamp: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)

class Exposure(Base):
    __tablename__ = "exposures"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    lob: Mapped[str] = mapped_column(String)
    subclass: Mapped[str | None] = mapped_column(String, nullable=True)
    account_id: Mapped[str | None] = mapped_column(String, nullable=True)
    treaty_id: Mapped[str | None] = mapped_column(String, nullable=True)
    layer_id: Mapped[str | None] = mapped_column(String, nullable=True)
    jurisdiction: Mapped[str | None] = mapped_column(String, nullable=True)
    geography: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))

class Binding(Base):
    __tablename__ = "bindings"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    audit_id: Mapped[str] = mapped_column(String)
    bound_by: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
