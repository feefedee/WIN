from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class SeverityLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Patient(Base):
    __tablename__ = "patients"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    age        = Column(Integer)
    blood_type = Column(String)
    conditions = Column(Text)           # comma-separated existing conditions
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    records    = relationship("HealthRecord", back_populates="patient")
    owner      = relationship("User", backref="patient_profile")


class HealthRecord(Base):
    __tablename__ = "health_records"

    id          = Column(Integer, primary_key=True, index=True)
    patient_id  = Column(Integer, ForeignKey("patients.id"))
    title       = Column(String, nullable=False)      # e.g. "Blood Test", "Symptom Check"
    description = Column(Text)
    severity    = Column(Enum(SeverityLevel), default=SeverityLevel.low)
    heart_rate  = Column(Float, nullable=True)
    bp_systolic = Column(Float, nullable=True)
    bp_diastolic= Column(Float, nullable=True)
    notes       = Column(Text, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    patient     = relationship("Patient", back_populates="records")


class Appointment(Base):
    __tablename__ = "appointments"

    id           = Column(Integer, primary_key=True, index=True)
    patient_id   = Column(Integer, ForeignKey("patients.id"))
    doctor_name  = Column(String)
    specialty    = Column(String)
    scheduled_at = Column(DateTime(timezone=True))
    status       = Column(String, default="pending")  # pending, confirmed, cancelled
    notes        = Column(Text, nullable=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
