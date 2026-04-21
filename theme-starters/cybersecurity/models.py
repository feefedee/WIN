from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, Enum
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class ThreatLevel(str, enum.Enum):
    info = "info"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ThreatLog(Base):
    __tablename__ = "threat_logs"

    id           = Column(Integer, primary_key=True, index=True)
    ip_address   = Column(String)
    event_type   = Column(String)        # e.g. brute_force, sql_injection, xss
    payload      = Column(Text)          # raw suspicious input
    threat_level = Column(Enum(ThreatLevel), default=ThreatLevel.low)
    blocked      = Column(Boolean, default=False)
    user_agent   = Column(String, nullable=True)
    endpoint     = Column(String, nullable=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())


class PasswordAudit(Base):
    __tablename__ = "password_audits"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer)
    score       = Column(Integer)        # 0-100
    feedback    = Column(Text)           # what's weak
    checked_at  = Column(DateTime(timezone=True), server_default=func.now())


class VulnReport(Base):
    __tablename__ = "vuln_reports"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String)
    description = Column(Text)
    severity    = Column(Enum(ThreatLevel))
    url         = Column(String, nullable=True)
    status      = Column(String, default="open")   # open, investigating, resolved
    reported_by = Column(Integer)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
