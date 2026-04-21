from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.db.database import get_db
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()

# ── Schemas ───────────────────────────────────────────────────────

class IssueCreate(BaseModel):
    category: str
    title: str
    description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    image_url: Optional[str] = None
    priority: Optional[str] = "medium"

class IssueStatusUpdate(BaseModel):
    status: str

class TrafficLogCreate(BaseModel):
    location: str
    congestion: int         # 0-100
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    avg_speed_kmh: Optional[float] = None
    incident: Optional[str] = None

class BusStopCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    routes: str             # e.g. "12A, 34B, 7"

class AlertCreate(BaseModel):
    alert_type: str
    title: str
    message: str
    area: str
    expires_at: Optional[datetime] = None

# ── Routes ────────────────────────────────────────────────────────

@router.post("/issues")
def report_issue(data: IssueCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.smartcities.models import CityIssue
    issue = CityIssue(**data.model_dump(), reported_by=user.id)
    db.add(issue); db.commit(); db.refresh(issue)
    return issue

@router.get("/issues")
def list_issues(category: Optional[str] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    from extra_starters.smartcities.models import CityIssue
    q = db.query(CityIssue)
    if category: q = q.filter(CityIssue.category == category)
    if status:   q = q.filter(CityIssue.status == status)
    return q.order_by(CityIssue.created_at.desc()).all()

@router.put("/issues/{issue_id}/status")
def update_issue_status(issue_id: int, data: IssueStatusUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.smartcities.models import CityIssue
    issue = db.query(CityIssue).filter(CityIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(404, "Issue not found")
    issue.status = data.status
    if data.status == "resolved":
        issue.resolved_at = datetime.utcnow()
    db.commit(); db.refresh(issue)
    return issue

@router.post("/issues/{issue_id}/upvote")
def upvote_issue(issue_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.smartcities.models import CityIssue
    issue = db.query(CityIssue).filter(CityIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(404, "Issue not found")
    issue.upvotes += 1
    db.commit()
    return {"upvotes": issue.upvotes}

@router.post("/traffic")
def log_traffic(data: TrafficLogCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.smartcities.models import TrafficLog
    log = TrafficLog(**data.model_dump())
    db.add(log); db.commit(); db.refresh(log)
    return log

@router.get("/traffic")
def get_traffic(location: Optional[str] = None, db: Session = Depends(get_db)):
    from extra_starters.smartcities.models import TrafficLog
    q = db.query(TrafficLog)
    if location: q = q.filter(TrafficLog.location.ilike(f"%{location}%"))
    return q.order_by(TrafficLog.recorded_at.desc()).limit(50).all()

@router.post("/bus-stops")
def add_bus_stop(data: BusStopCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.smartcities.models import BusStop
    stop = BusStop(**data.model_dump())
    db.add(stop); db.commit(); db.refresh(stop)
    return stop

@router.get("/bus-stops")
def list_bus_stops(db: Session = Depends(get_db)):
    from extra_starters.smartcities.models import BusStop
    return db.query(BusStop).filter(BusStop.is_active == True).all()

@router.post("/alerts")
def create_alert(data: AlertCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.smartcities.models import PublicAlert
    alert = PublicAlert(**data.model_dump(), issued_by=user.id)
    db.add(alert); db.commit(); db.refresh(alert)
    return alert

@router.get("/alerts")
def list_alerts(db: Session = Depends(get_db)):
    from extra_starters.smartcities.models import PublicAlert
    return db.query(PublicAlert).filter(PublicAlert.is_active == True).all()
