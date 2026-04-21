from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import re

from app.db.database import get_db
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()

# ── Schemas ───────────────────────────────────────────────────────

class ThreatLogCreate(BaseModel):
    ip_address: str
    event_type: str
    payload: str
    threat_level: Optional[str] = "low"
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None

class PasswordCheckRequest(BaseModel):
    password: str

class VulnReportCreate(BaseModel):
    title: str
    description: str
    severity: str
    url: Optional[str] = None

# ── Utilities ─────────────────────────────────────────────────────

def score_password(password: str) -> dict:
    score = 0
    feedback = []
    if len(password) >= 8:  score += 20
    else: feedback.append("Too short — use at least 8 characters")
    if re.search(r"[A-Z]", password): score += 20
    else: feedback.append("Add uppercase letters")
    if re.search(r"[a-z]", password): score += 20
    else: feedback.append("Add lowercase letters")
    if re.search(r"\d", password): score += 20
    else: feedback.append("Add numbers")
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): score += 20
    else: feedback.append("Add special characters")
    return {"score": score, "feedback": feedback, "strength": (
        "very weak" if score < 40 else
        "weak" if score < 60 else
        "fair" if score < 80 else
        "strong" if score < 100 else "very strong"
    )}

def detect_threats(payload: str) -> str:
    payload_lower = payload.lower()
    if any(x in payload_lower for x in ["select ", "union ", "drop ", "insert ", "--", "1=1"]):
        return "sql_injection"
    if any(x in payload_lower for x in ["<script", "javascript:", "onerror=", "onload="]):
        return "xss"
    if any(x in payload_lower for x in ["../", "..\\", "/etc/passwd"]):
        return "path_traversal"
    return "suspicious_input"

# ── Routes ────────────────────────────────────────────────────────

@router.post("/log-threat")
def log_threat(data: ThreatLogCreate, db: Session = Depends(get_db)):
    from theme_starters.cybersecurity.models import ThreatLog
    log = ThreatLog(**data.model_dump())
    db.add(log); db.commit(); db.refresh(log)
    return log

@router.get("/threats")
def get_threats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.cybersecurity.models import ThreatLog
    return db.query(ThreatLog).order_by(ThreatLog.created_at.desc()).limit(100).all()

@router.post("/check-password")
def check_password(data: PasswordCheckRequest):
    return score_password(data.password)

@router.post("/scan-input")
def scan_input(data: dict):
    payload = str(data.get("input", ""))
    threat = detect_threats(payload)
    return {"input": payload, "threat_detected": threat != "suspicious_input" or False, "threat_type": threat}

@router.post("/report-vuln")
def report_vuln(data: VulnReportCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.cybersecurity.models import VulnReport
    report = VulnReport(**data.model_dump(), reported_by=user.id)
    db.add(report); db.commit(); db.refresh(report)
    return report

@router.get("/reports")
def list_reports(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from theme_starters.cybersecurity.models import VulnReport
    return db.query(VulnReport).all()
