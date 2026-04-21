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

class FarmCreate(BaseModel):
    name: str
    location: str
    area_acres: float
    soil_type: Optional[str] = None

class CropCreate(BaseModel):
    farm_id: int
    name: str
    variety: Optional[str] = None
    planted_at: Optional[datetime] = None
    expected_harvest: Optional[datetime] = None
    area_acres: float

class CropLogCreate(BaseModel):
    crop_id: int
    log_type: str        # irrigation, fertilizer, pesticide, observation
    description: str
    quantity: Optional[float] = None
    unit: Optional[str] = None

class WeatherLogCreate(BaseModel):
    farm_id: int
    temperature: float
    humidity: float
    rainfall_mm: Optional[float] = None
    wind_speed: Optional[float] = None
    condition: Optional[str] = None

class MarketPriceCreate(BaseModel):
    crop_name: str
    price_per_kg: float
    market: str

# ── Routes ────────────────────────────────────────────────────────

@router.post("/farms")
def create_farm(data: FarmCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.agritech.models import Farm
    farm = Farm(**data.model_dump(), user_id=user.id)
    db.add(farm); db.commit(); db.refresh(farm)
    return farm

@router.get("/farms")
def list_farms(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.agritech.models import Farm
    return db.query(Farm).filter(Farm.user_id == user.id).all()

@router.post("/crops")
def add_crop(data: CropCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.agritech.models import Crop
    crop = Crop(**data.model_dump())
    db.add(crop); db.commit(); db.refresh(crop)
    return crop

@router.get("/crops/{farm_id}")
def list_crops(farm_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.agritech.models import Crop
    return db.query(Crop).filter(Crop.farm_id == farm_id).all()

@router.put("/crops/{crop_id}/status")
def update_crop_status(crop_id: int, status: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.agritech.models import Crop
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(404, "Crop not found")
    crop.status = status
    db.commit(); db.refresh(crop)
    return crop

@router.post("/logs")
def add_crop_log(data: CropLogCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.agritech.models import CropLog
    log = CropLog(**data.model_dump())
    db.add(log); db.commit(); db.refresh(log)
    return log

@router.get("/logs/{crop_id}")
def get_crop_logs(crop_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.agritech.models import CropLog
    return db.query(CropLog).filter(CropLog.crop_id == crop_id).all()

@router.post("/weather")
def log_weather(data: WeatherLogCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.agritech.models import WeatherLog
    log = WeatherLog(**data.model_dump())
    db.add(log); db.commit(); db.refresh(log)
    return log

@router.get("/weather/{farm_id}")
def get_weather(farm_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.agritech.models import WeatherLog
    return db.query(WeatherLog).filter(WeatherLog.farm_id == farm_id).order_by(WeatherLog.recorded_at.desc()).limit(30).all()

@router.post("/market-prices")
def add_price(data: MarketPriceCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from extra_starters.agritech.models import MarketPrice
    price = MarketPrice(**data.model_dump())
    db.add(price); db.commit(); db.refresh(price)
    return price

@router.get("/market-prices")
def get_prices(crop: Optional[str] = None, db: Session = Depends(get_db)):
    from extra_starters.agritech.models import MarketPrice
    q = db.query(MarketPrice)
    if crop:
        q = q.filter(MarketPrice.crop_name.ilike(f"%{crop}%"))
    return q.order_by(MarketPrice.updated_at.desc()).all()
