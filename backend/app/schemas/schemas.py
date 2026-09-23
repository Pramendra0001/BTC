from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional, Any, Dict, Union
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "VIEWER"
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class PublicUserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username (3-50 characters)")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=128, description="Secure password (minimum 8 characters)")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        weak_defaults = {"admin123", "changeme123", "password123", "12345678", "password", "qwerty123"}
        if v.lower() in weak_defaults:
            raise ValueError("Password is too common or predictable. Please choose a stronger password.")
        return v

UserRegister = PublicUserRegister

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class DatasetBase(BaseModel):
    name: str
    filename: str
    format: Optional[str] = None

class DatasetResponse(DatasetBase):
    id: int
    status: str
    total_records: int
    valid_records: int
    invalid_records: int
    duplicate_records: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class DatasetUploadResponse(BaseModel):
    message: str
    dataset: DatasetResponse

class DatasetListResponse(BaseModel):
    datasets: List[DatasetResponse]

class TransactionResponse(BaseModel):
    id: int
    txid: str
    timestamp: datetime
    fee: float
    script_type: str
    total_input: float
    total_output: float
    class Config:
        from_attributes = True

class TransactionInputResponse(BaseModel):
    wallet_address: str
    amount: float
    position: int
    class Config:
        from_attributes = True

class TransactionOutputResponse(BaseModel):
    wallet_address: str
    amount: float
    position: int
    class Config:
        from_attributes = True

class TransactionDetailResponse(TransactionResponse):
    inputs: List[TransactionInputResponse]
    outputs: List[TransactionOutputResponse]

class WalletResponse(BaseModel):
    address: str
    first_seen: datetime
    last_seen: datetime
    total_sent: float
    total_received: float
    tx_count: int
    class Config:
        from_attributes = True

class WalletDetailResponse(WalletResponse):
    recent_transactions: List[TransactionResponse] = []

class IPEntityResponse(BaseModel):
    ip_address: str
    first_seen: datetime
    last_seen: datetime
    observation_count: int
    asn: Optional[str]
    country: Optional[str]
    class Config:
        from_attributes = True

class ASNEntityResponse(BaseModel):
    asn_number: str
    name: Optional[str]
    country_count: int
    ip_count: int
    class Config:
        from_attributes = True

class AlertResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: str
    priority: str
    anomaly_score: float
    confidence: Optional[float] = 0.0
    status: str
    review_state: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class AlertDetailResponse(AlertResponse):
    contributing_signals: Optional[Union[Dict[str, Any], List[Any]]] = None
    evidence_ids: Optional[List[int]] = None

class AlertListResponse(BaseModel):
    alerts: List[AlertResponse]
    total: int

class EvidenceResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: str
    category: str
    observation: str
    strength: float
    created_at: datetime
    details: Dict[str, Any]
    class Config:
        from_attributes = True

class CaseBase(BaseModel):
    title: str
    description: str
    priority: str = "MEDIUM"
    status: str = "OPEN"

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class CaseResponse(CaseBase):
    id: int
    investigator_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class CaseNoteCreate(BaseModel):
    content: str

class CaseNoteResponse(BaseModel):
    id: int
    case_id: int
    user_id: int
    content: str
    created_at: datetime
    class Config:
        from_attributes = True

class CaseDetailResponse(CaseResponse):
    entities: List[Dict[str, Any]] = []
    evidence: List[Dict[str, Any]] = []
    notes: List[CaseNoteResponse] = []

class GraphNodeResponse(BaseModel):
    id: str
    type: str
    label: str
    properties: Dict[str, Any]

class GraphEdgeResponse(BaseModel):
    id: str
    source: str
    target: str
    type: str
    weight: float
    properties: Dict[str, Any]

class GraphResponse(BaseModel):
    nodes: List[GraphNodeResponse]
    edges: List[GraphEdgeResponse]

class TimelineEventResponse(BaseModel):
    timestamp: Optional[Union[datetime, str]] = None
    event_type: Optional[str] = None
    type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class TimelineResponse(BaseModel):
    entity_type: str
    entity_id: str
    events: List[TimelineEventResponse]

class SearchResultResponse(BaseModel):
    entity_type: str
    entity_id: str
    label: str
    match_score: float
    details: Dict[str, Any]

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultResponse]

class DashboardStats(BaseModel):
    totalTx: int = 0
    activeWallets: int = 0
    monitoredIps: int = 0
    activeAlerts: int = 0
    totalAsns: int = 0
    totalObservations: int = 0
    openCases: int = 0
    totalEvidence: int = 0
    totalDatasets: int = 0

class DashboardAlerts(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    new: int = 0
    reviewing: int = 0
    resolved: int = 0

class DashboardCases(BaseModel):
    open: int = 0
    active: int = 0
    closed: int = 0

class DashboardResponse(BaseModel):
    stats: DashboardStats
    alerts: DashboardAlerts
    cases: DashboardCases
    anomalyDistribution: Dict[str, int] = {}
    recentAlerts: List[Dict[str, Any]] = []
    processingStatus: Dict[str, int] = {}
    modelInfo: Dict[str, Any] = {}

class SystemStatusResponse(BaseModel):
    database: str
    ml_service: str
    ai_provider: str
    uptime_seconds: int

class HealthResponse(BaseModel):
    status: str

class ModelRunResponse(BaseModel):
    id: int
    model_type: str
    model_version: str
    status: str
    parameters: Optional[Dict[str, Any]] = None
    evaluation_metrics: Optional[Dict[str, Any]] = None
    created_at: datetime
    class Config:
        from_attributes = True

class DataQualityResponse(BaseModel):
    dataset_id: int
    total_records: int
    valid_records: int
    invalid_records: int
    duplicate_records: int

class ReportResponse(BaseModel):
    case_id: int
    title: str
    report_content: str
    generated_at: datetime

class AIInterpretationResponse(BaseModel):
    entity_type: str
    entity_id: str
    summary: str
    observations: List[str]
    contributing_signals: List[Dict[str, Any]]
    recommended_review_actions: List[str]
    uncertainty: str
    insufficient_information: List[str]

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
