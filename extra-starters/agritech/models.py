from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base


class CropStatus(str, enum.Enum):
    planted = "planted"
    growing = "growing"
    ready   = "ready"
    harvested = "harvested"


class Farm(Base):
    __tablename__ = "farms"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    name       = Column(String)
    location   = Column(String)
    area_acres = Column(Float)
    soil_type  = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    crops      = relationship("Crop", back_populates="farm")


class Crop(Base):
    __tablename__ = "crops"

    id          = Column(Integer, primary_key=True, index=True)
    farm_id     = Column(Integer, ForeignKey("farms.id"))
    name        = Column(String)           # e.g. "Wheat", "Rice"
    variety     = Column(String, nullable=True)
    planted_at  = Column(DateTime(timezone=True), nullable=True)
    expected_harvest = Column(DateTime(timezone=True), nullable=True)
    status      = Column(Enum(CropStatus), default=CropStatus.planted)
    area_acres  = Column(Float)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    farm        = relationship("Farm", back_populates="crops")
    logs        = relationship("CropLog", back_populates="crop")


class CropLog(Base):
    __tablename__ = "crop_logs"

    id           = Column(Integer, primary_key=True, index=True)
    crop_id      = Column(Integer, ForeignKey("crops.id"))
    log_type     = Column(String)    # irrigation, fertilizer, pesticide, observation
    description  = Column(Text)
    quantity     = Column(Float, nullable=True)
    unit         = Column(String, nullable=True)   # liters, kg, etc.
    logged_at    = Column(DateTime(timezone=True), server_default=func.now())

    crop         = relationship("Crop", back_populates="logs")


class WeatherLog(Base):
    __tablename__ = "weather_logs"

    id            = Column(Integer, primary_key=True, index=True)
    farm_id       = Column(Integer, ForeignKey("farms.id"))
    temperature   = Column(Float)
    humidity      = Column(Float)
    rainfall_mm   = Column(Float, nullable=True)
    wind_speed    = Column(Float, nullable=True)
    condition     = Column(String, nullable=True)   # sunny, cloudy, rainy
    recorded_at   = Column(DateTime(timezone=True), server_default=func.now())


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id          = Column(Integer, primary_key=True, index=True)
    crop_name   = Column(String, index=True)
    price_per_kg= Column(Float)
    market      = Column(String)
    updated_at  = Column(DateTime(timezone=True), server_default=func.now())
