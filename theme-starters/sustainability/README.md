# Theme: Sustainability & Social Impact

## Likely problem statements
- Carbon footprint tracker
- Waste management / reporting system
- Green challenge & gamification app
- Community environmental alerts
- Eco-score for daily habits

## Your models (already built)
- CarbonLog — category, activity, auto-calculated CO2 kg
- WasteReport — location, type, quantity, status
- GreenChallenge — title, points, category
- UserChallenge — tracks which user completed which challenge

## Endpoints
| Method | URL | Description |
|--------|-----|-------------|
| POST | /eco/carbon | Log a carbon activity (auto-calculates CO2) |
| GET  | /eco/carbon/total | Total CO2 + breakdown by category |
| POST | /eco/waste | Report waste at a location |
| GET  | /eco/waste | View all waste reports |
| GET  | /eco/challenges | List all green challenges |
| POST | /eco/challenges/{id}/complete | Mark challenge done |

## Built-in CO2 factors (kg per unit)
- car_km → 0.21 kg
- flight_km → 0.255 kg
- beef_kg → 27.0 kg
- chicken_kg → 6.9 kg
- electricity_kwh → 0.82 kg

## How to plug into main.py
```python
from theme_starters.sustainability.routes import router as eco_router
app.include_router(eco_router, prefix="/eco", tags=["Sustainability"])
```
