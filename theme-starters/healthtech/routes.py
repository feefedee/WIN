from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.db.database import get_db
from app.models.user import User
from app.core.security import get_current_user

# ── Pydantic schemas ──────────────────────────────────────────────

class PatientCreate(BaseModel):
    age: int
    blood_type: str
    conditions: Optional[str] = ""

class RecordCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: Optional[str] = "low"
    heart_rate: Optional[float] = None
    bp_systolic: Optional[float] = None
    bp_diastolic: Optional[float] = None
    notes: Optional[str] = None

class AppointmentCreate(BaseModel):
    doctor_name: str
    specialty: str
    scheduled_at: datetime
    notes: Optional[str] = None

# ── Router ────────────────────────────────────────────────────────

router = APIRouter()

@router.post("/patient")
def create_patient(data: PatientCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.healthtech.models import Patient
    patient = Patient(**data.model_dump(), user_id=user.id)
    db.add(patient); db.commit(); db.refresh(patient)
    return patient

@router.post("/records/{patient_id}")
def add_record(patient_id: int, data: RecordCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.healthtech.models import HealthRecord
    record = HealthRecord(**data.model_dump(), patient_id=patient_id)
    db.add(record); db.commit(); db.refresh(record)
    return record

@router.get("/records/{patient_id}")
def get_records(patient_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.healthtech.models import HealthRecord
    return db.query(HealthRecord).filter(HealthRecord.patient_id == patient_id).all()

@router.post("/appointments")
def book_appointment(data: AppointmentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.healthtech.models import Appointment, Patient
    patient = db.query(Patient).filter(Patient.user_id == user.id).first()
    if not patient:
        raise HTTPException(404, "Create a patient profile first")
    appt = Appointment(**data.model_dump(), patient_id=patient.id)
    db.add(appt); db.commit(); db.refresh(appt)
    return appt

@router.get("/appointments")
def list_appointments(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.healthtech.models import Appointment, Patient
    patient = db.query(Patient).filter(Patient.user_id == user.id).first()
    if not patient:
        return []
    return db.query(Appointment).filter(Appointment.patient_id == patient.id).all()
