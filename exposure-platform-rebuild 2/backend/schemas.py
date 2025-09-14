
from pydantic import BaseModel, Field
from typing import Any, Optional, List, Dict

class AuditEventIn(BaseModel):
    type: str
    user: Optional[str] = None
    role: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class AuditEventOut(BaseModel):
    id: int
    type: str
    user_name: Optional[str]
    user_role: Optional[str]
    timestamp: str
    payload: Optional[Dict[str, Any]]

class ExposureIn(BaseModel):
    lob: str
    subclass: Optional[str] = None
    account_id: Optional[str] = None
    treaty_id: Optional[str] = None
    layer_id: Optional[str] = None
    jurisdiction: Optional[str] = None
    geography: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None

class ExposureOut(ExposureIn):
    id: int
    created_at: str

class ConfigOut(BaseModel):
    metadata: Dict[str, Any]
    targets: Dict[str, Any]
    jurisdiction_overrides: Dict[str, Any]
    classes: Dict[str, Any]

class QuoteRequest(BaseModel):
    jurisdiction: str
    class_: str = Field(alias="class")
    product: str
    program: str
    exposure: Dict[str, Any]
    risk_factors: Dict[str, Any] = {}
    loss_history: List[Dict[str, Any]] = []
    options: Dict[str, Any] = {}

class QuoteResponse(BaseModel):
    technical_premium: float
    components: Dict[str, float]
    decision: str
    reasons: List[str] = []
    warnings: List[str] = []
    audit_id: str
