from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class TransactionType(str, enum.Enum):
    credit = "credit"
    debit  = "debit"

class TransactionStatus(str, enum.Enum):
    pending   = "pending"
    completed = "completed"
    failed    = "failed"
    flagged   = "flagged"


class Wallet(Base):
    __tablename__ = "wallets"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), unique=True)
    balance    = Column(Float, default=0.0)
    currency   = Column(String, default="INR")
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transactions = relationship("Transaction", back_populates="wallet")


class Transaction(Base):
    __tablename__ = "transactions"

    id           = Column(Integer, primary_key=True, index=True)
    wallet_id    = Column(Integer, ForeignKey("wallets.id"))
    type         = Column(Enum(TransactionType))
    amount       = Column(Float)
    description  = Column(String)
    category     = Column(String, nullable=True)   # food, travel, shopping, etc.
    reference_id = Column(String, nullable=True)   # unique transaction ref
    status       = Column(Enum(TransactionStatus), default=TransactionStatus.completed)
    fraud_score  = Column(Float, default=0.0)      # 0-100, higher = more suspicious
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    wallet       = relationship("Wallet", back_populates="transactions")


class FraudAlert(Base):
    __tablename__ = "fraud_alerts"

    id             = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    reason         = Column(Text)
    score          = Column(Float)
    reviewed       = Column(Boolean, default=False)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())


class Loan(Base):
    __tablename__ = "loans"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"))
    amount       = Column(Float)
    interest_rate= Column(Float)
    tenure_months= Column(Integer)
    emi          = Column(Float)
    status       = Column(String, default="pending")   # pending, approved, rejected, active
    applied_at   = Column(DateTime(timezone=True), server_default=func.now())
