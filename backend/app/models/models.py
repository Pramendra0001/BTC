from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum

class RoleEnum(str, enum.Enum):
    ADMINISTRATOR = "ADMINISTRATOR"
    INVESTIGATOR = "INVESTIGATOR"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default=RoleEnum.VIEWER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    format = Column(String)
    status = Column(String, default="PENDING")
    total_records = Column(Integer, default=0)
    valid_records = Column(Integer, default=0)
    invalid_records = Column(Integer, default=0)
    duplicate_records = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RawRecord(Base):
    __tablename__ = "raw_records"
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    line_number = Column(Integer)
    raw_data = Column(JSON)
    is_valid = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    txid = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, index=True)
    fee = Column(Float)
    script_type = Column(String)
    total_input = Column(Float)
    total_output = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    inputs = relationship("TransactionInput", back_populates="transaction")
    outputs = relationship("TransactionOutput", back_populates="transaction")

class TransactionInput(Base):
    __tablename__ = "transaction_inputs"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), index=True)
    wallet_address = Column(String, index=True)
    amount = Column(Float)
    position = Column(Integer)
    
    transaction = relationship("Transaction", back_populates="inputs")

class TransactionOutput(Base):
    __tablename__ = "transaction_outputs"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), index=True)
    wallet_address = Column(String, index=True)
    amount = Column(Float)
    position = Column(Integer)
    
    transaction = relationship("Transaction", back_populates="outputs")

class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, unique=True, index=True)
    wallet_type = Column(String, nullable=True)
    country = Column(String, nullable=True)
    synthetic_balance_sats = Column(Float, nullable=True)
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    total_sent = Column(Float, default=0)
    total_received = Column(Float, default=0)
    tx_count = Column(Integer, default=0, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class NetworkObservation(Base):
    __tablename__ = "network_observations"
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    transaction_id = Column(String, index=True)
    src_ip = Column(String, index=True)
    dst_ip = Column(String)
    src_port = Column(Integer)
    dst_port = Column(Integer)
    timestamp = Column(DateTime)
    geo_country = Column(String)
    asn = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class IPEntity(Base):
    __tablename__ = "ip_entities"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, unique=True, index=True)
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    observation_count = Column(Integer, default=0)
    asn = Column(String)
    country = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ASNEntity(Base):
    __tablename__ = "asn_entities"
    id = Column(Integer, primary_key=True, index=True)
    asn_number = Column(String, unique=True, index=True)
    name = Column(String)
    country_count = Column(Integer, default=0)
    ip_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class BehavioralFeature(Base):
    __tablename__ = "behavioral_features"
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, index=True)
    entity_id = Column(String, index=True)
    feature_schema_version = Column(String)
    features = Column(JSON)
    computed_at = Column(DateTime, default=datetime.utcnow)

class ModelRun(Base):
    __tablename__ = "model_runs"
    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(String)
    model_version = Column(String)
    feature_schema_version = Column(String)
    parameters = Column(JSON)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    training_timestamp = Column(DateTime)
    evaluation_metrics = Column(JSON)
    artifact_path = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class AnomalyResult(Base):
    __tablename__ = "anomaly_results"
    id = Column(Integer, primary_key=True, index=True)
    model_run_id = Column(Integer, ForeignKey("model_runs.id"))
    entity_type = Column(String, index=True)
    entity_id = Column(String, index=True)
    anomaly_score = Column(Float)
    cluster_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, index=True)
    entity_id = Column(String, index=True)
    category = Column(String)
    observation = Column(Text)
    details = Column(JSON)
    source_dataset_id = Column(Integer)
    source_record_id = Column(Integer)
    strength = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, index=True)
    entity_id = Column(String, index=True)
    priority = Column(String, index=True)
    anomaly_score = Column(Float)
    confidence = Column(Float)
    model_version = Column(String)
    contributing_signals = Column(JSON)
    evidence_ids = Column(JSON)
    status = Column(String, default="NEW", index=True)
    review_state = Column(String, default="UNREVIEWED")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    status = Column(String, default="OPEN")
    priority = Column(String, default="MEDIUM")
    investigator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CaseEntity(Base):
    __tablename__ = "case_entities"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    entity_type = Column(String)
    entity_id = Column(String)
    added_at = Column(DateTime, default=datetime.utcnow)

class CaseEvidence(Base):
    __tablename__ = "case_evidence"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    evidence_id = Column(Integer, ForeignKey("evidence.id"))
    added_at = Column(DateTime, default=datetime.utcnow)

class CaseNote(Base):
    __tablename__ = "case_notes"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(String)
    details = Column(JSON)
    ip_address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class GraphNode(Base):
    __tablename__ = "graph_nodes"
    id = Column(Integer, primary_key=True, index=True)
    node_type = Column(String)
    node_id = Column(String, index=True)
    label = Column(String)
    properties = Column(JSON)

class GraphEdge(Base):
    __tablename__ = "graph_edges"
    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String, index=True)
    source_id = Column(String, index=True)
    target_type = Column(String, index=True)
    target_id = Column(String, index=True)
    edge_type = Column(String, index=True)
    weight = Column(Float, default=1.0)
    properties = Column(JSON)
    provenance = Column(String)
