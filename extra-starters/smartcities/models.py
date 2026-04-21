from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class IssueStatus(str, enum.Enum):
    open        = "open"
    in_progress = "in_progress"
    resolved    = "resolved"

class IssuePriority(str, enum.Enum):
    low      = "low"
    medium   = "medium"
    high     = "high"
    critical = "critical"


class CityIssue(Base):
    """Citizen-reported city problems — potholes, broken lights, water leaks etc."""
    __tablename__ = "city_issues"

    id          = Column(Integer, primary_key=True, index=True)
    reported_by = Column(Integer, ForeignKey("users.id"))
    category    = Column(String)        # road, water, electricity, garbage, safety
    title       = Column(String)
    description = Column(Text)
    latitude    = Column(Float, nullable=True)
    longitude   = Column(Float, nullable=True)
    address     = Column(String, nullable=True)
    image_url   = Column(String, nullable=True)
    status      = Column(Enum(IssueStatus), default=IssueStatus.open)
    priority    = Column(Enum(IssuePriority), default=IssuePriority.medium)
    upvotes     = Column(Integer, default=0)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class TrafficLog(Base):
    __tablename__ = "traffic_logs"

    id           = Column(Integer, primary_key=True, index=True)
    location     = Column(String)
    latitude     = Column(Float, nullable=True)
    longitude    = Column(Float, nullable=True)
    congestion   = Column(Integer)      # 0-100 scale
    avg_speed_kmh= Column(Float, nullable=True)
    incident     = Column(String, nullable=True)   # accident, roadwork, event
    recorded_at  = Column(DateTime(timezone=True), server_default=func.now())


class BusStop(Base):
    __tablename__ = "bus_stops"

    id        = Column(Integer, primary_key=True, index=True)
    name      = Column(String)
    latitude  = Column(Float)
    longitude = Column(Float)
    routes    = Column(String)          # comma-separated route numbers
    is_active = Column(Boolean, default=True)


class PublicAlert(Base):
    __tablename__ = "public_alerts"

    id          = Column(Integer, primary_key=True, index=True)
    issued_by   = Column(Integer, ForeignKey("users.id"))
    alert_type  = Column(String)        # weather, traffic, safety, utility
    title       = Column(String)
    message     = Column(Text)
    area        = Column(String)
    is_active   = Column(Boolean, default=True)
    expires_at  = Column(DateTime(timezone=True), nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
