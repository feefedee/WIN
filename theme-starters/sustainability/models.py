from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class CarbonLog(Base):
    __tablename__ = "carbon_logs"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"))
    category     = Column(String)    # transport, food, energy, shopping
    activity     = Column(String)    # e.g. "drove 20km", "ate beef"
    co2_kg       = Column(Float)     # calculated CO2 in kg
    notes        = Column(Text, nullable=True)
    logged_at    = Column(DateTime(timezone=True), server_default=func.now())


class WasteReport(Base):
    __tablename__ = "waste_reports"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"))
    location     = Column(String)
    waste_type   = Column(String)    # plastic, organic, e-waste, hazardous
    quantity_kg  = Column(Float)
    image_url    = Column(String, nullable=True)
    status       = Column(String, default="reported")  # reported, in_progress, resolved
    created_at   = Column(DateTime(timezone=True), server_default=func.now())


class GreenChallenge(Base):
    __tablename__ = "green_challenges"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String)
    description = Column(Text)
    points      = Column(Integer, default=10)
    category    = Column(String)


class UserChallenge(Base):
    __tablename__ = "user_challenges"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"))
    challenge_id = Column(Integer, ForeignKey("green_challenges.id"))
    completed    = Column(Integer, default=0)  # 0 or 1
    completed_at = Column(DateTime(timezone=True), nullable=True)
