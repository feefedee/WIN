from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.db.database import get_db
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()

# ── CO2 emission factors (kg per unit) ───────────────────────────
CO2_FACTORS = {
    "car_km": 0.21,
    "flight_km": 0.255,
    "beef_kg": 27.0,
    "chicken_kg": 6.9,
    "electricity_kwh": 0.82,
    "plastic_bag": 0.006,
}

# ── Schemas ───────────────────────────────────────────────────────

class CarbonLogCreate(BaseModel):
    category: str
    activity: str
    activity_type: str       # must match a key in CO2_FACTORS
    quantity: float
    notes: Optional[str] = None

class WasteReportCreate(BaseModel):
    location: str
    waste_type: str
    quantity_kg: float
    image_url: Optional[str] = None

class ChallengeCreate(BaseModel):
    title: str
    description: str
    points: int = 10
    category: str

# ── Routes ────────────────────────────────────────────────────────

@router.post("/carbon")
def log_carbon(data: CarbonLogCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.sustainability.models import CarbonLog
    factor = CO2_FACTORS.get(data.activity_type, 1.0)
    co2 = round(factor * data.quantity, 3)
    log = CarbonLog(
        user_id=user.id,
        category=data.category,
        activity=data.activity,
        co2_kg=co2,
        notes=data.notes
    )
    db.add(log); db.commit(); db.refresh(log)
    return {**log.__dict__, "co2_kg": co2}

@router.get("/carbon/total")
def total_carbon(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.sustainability.models import CarbonLog
    logs = db.query(CarbonLog).filter(CarbonLog.user_id == user.id).all()
    total = sum(l.co2_kg for l in logs)
    by_category = {}
    for l in logs:
        by_category[l.category] = round(by_category.get(l.category, 0) + l.co2_kg, 3)
    return {"total_co2_kg": round(total, 3), "by_category": by_category, "logs": logs}

@router.post("/waste")
def report_waste(data: WasteReportCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.sustainability.models import WasteReport
    report = WasteReport(**data.model_dump(), user_id=user.id)
    db.add(report); db.commit(); db.refresh(report)
    return report

@router.get("/waste")
def list_waste(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.sustainability.models import WasteReport
    return db.query(WasteReport).all()

@router.post("/challenges")
def create_challenge(data: ChallengeCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.sustainability.models import GreenChallenge
    c = GreenChallenge(**data.model_dump())
    db.add(c); db.commit(); db.refresh(c)
    return c

@router.get("/challenges")
def list_challenges(db: Session = Depends(get_db)):
    from theme_starters.sustainability.models import GreenChallenge
    return db.query(GreenChallenge).all()

@router.post("/challenges/{challenge_id}/complete")
def complete_challenge(challenge_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.sustainability.models import UserChallenge
    uc = UserChallenge(user_id=user.id, challenge_id=challenge_id, completed=1, completed_at=datetime.utcnow())
    db.add(uc); db.commit()
    return {"message": "Challenge completed!", "challenge_id": challenge_id}
