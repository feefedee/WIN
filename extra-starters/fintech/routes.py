from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid

from app.db.database import get_db
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()

# ── Schemas ───────────────────────────────────────────────────────

class WalletTopup(BaseModel):
    amount: float

class TransferRequest(BaseModel):
    to_user_id: int
    amount: float
    description: Optional[str] = "Transfer"

class TransactionCreate(BaseModel):
    amount: float
    type: str                       # credit or debit
    description: str
    category: Optional[str] = None

class LoanApply(BaseModel):
    amount: float
    tenure_months: int

# ── Fraud detection ───────────────────────────────────────────────

def calculate_fraud_score(amount: float, user_id: int, db: Session) -> tuple[float, str]:
    from extra_starters.fintech.models import Transaction, Wallet
    reasons = []
    score = 0.0

    # Large amount flag
    if amount > 50000:
        score += 40
        reasons.append("Unusually large transaction amount")

    # Frequency check — more than 5 transactions in last hour
    from sqlalchemy import func as sqlfunc
    from datetime import datetime, timedelta
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if wallet:
        recent_count = db.query(Transaction).filter(
            Transaction.wallet_id == wallet.id,
            Transaction.created_at >= one_hour_ago
        ).count()
        if recent_count > 5:
            score += 35
            reasons.append("High transaction frequency")

    # Round number flag
    if amount % 1000 == 0 and amount >= 10000:
        score += 10
        reasons.append("Suspiciously round number")

    return round(score, 2), "; ".join(reasons) if reasons else "Clean"

# ── Routes ────────────────────────────────────────────────────────

@router.post("/wallet/create")
def create_wallet(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.fintech.models import Wallet
    existing = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if existing:
        return existing
    wallet = Wallet(user_id=user.id, balance=0.0)
    db.add(wallet); db.commit(); db.refresh(wallet)
    return wallet

@router.get("/wallet")
def get_wallet(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.fintech.models import Wallet
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if not wallet:
        raise HTTPException(404, "Wallet not found. Create one first.")
    return wallet

@router.post("/wallet/topup")
def topup_wallet(data: WalletTopup, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.fintech.models import Wallet, Transaction
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if not wallet:
        raise HTTPException(404, "Create wallet first")
    wallet.balance += data.amount
    txn = Transaction(
        wallet_id=wallet.id, type="credit",
        amount=data.amount, description="Wallet top-up",
        reference_id=str(uuid.uuid4())[:8]
    )
    db.add(txn); db.commit(); db.refresh(wallet)
    return {"balance": wallet.balance, "topped_up": data.amount}

@router.post("/transfer")
def transfer(data: TransferRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.fintech.models import Wallet, Transaction, FraudAlert
    sender_wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    receiver_wallet = db.query(Wallet).filter(Wallet.user_id == data.to_user_id).first()
    if not sender_wallet or not receiver_wallet:
        raise HTTPException(404, "Wallet not found")
    if sender_wallet.balance < data.amount:
        raise HTTPException(400, "Insufficient balance")

    # Fraud check
    score, reason = calculate_fraud_score(data.amount, user.id, db)
    status = "flagged" if score >= 50 else "completed"

    ref = str(uuid.uuid4())[:8]

    # Debit sender
    debit = Transaction(
        wallet_id=sender_wallet.id, type="debit",
        amount=data.amount, description=data.description,
        reference_id=ref, status=status, fraud_score=score
    )
    # Credit receiver
    credit = Transaction(
        wallet_id=receiver_wallet.id, type="credit",
        amount=data.amount, description=f"Received from user {user.id}",
        reference_id=ref, status=status
    )
    sender_wallet.balance -= data.amount
    receiver_wallet.balance += data.amount
    db.add_all([debit, credit]); db.flush()

    # Log fraud alert if needed
    if score >= 50:
        alert = FraudAlert(transaction_id=debit.id, reason=reason, score=score)
        db.add(alert)

    db.commit()
    return {"status": status, "reference": ref, "fraud_score": score, "amount": data.amount}

@router.get("/transactions")
def list_transactions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.fintech.models import Wallet, Transaction
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if not wallet:
        return []
    return db.query(Transaction).filter(Transaction.wallet_id == wallet.id).order_by(Transaction.created_at.desc()).all()

@router.get("/fraud-alerts")
def list_fraud_alerts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.fintech.models import FraudAlert
    return db.query(FraudAlert).filter(FraudAlert.reviewed == False).all()

@router.post("/loans/apply")
def apply_loan(data: LoanApply, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.fintech.models import Loan
    # Simple EMI formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    r = 0.01  # 1% monthly interest
    n = data.tenure_months
    emi = round(data.amount * r * (1 + r)**n / ((1 + r)**n - 1), 2)
    loan = Loan(user_id=user.id, amount=data.amount, interest_rate=12.0, tenure_months=n, emi=emi)
    db.add(loan); db.commit(); db.refresh(loan)
    return {"loan": loan, "monthly_emi": emi}
