# Theme: AgriTech

## Likely problem statements
- Smart crop monitoring dashboard
- Farmer market price tracker
- Irrigation & fertilizer log system
- Weather-based farming advisor
- Crop health & yield predictor

## Your models (already built)
- Farm — location, area, soil type
- Crop — name, variety, status (planted → growing → ready → harvested)
- CropLog — irrigation, fertilizer, pesticide, observation entries
- WeatherLog — temperature, humidity, rainfall per farm
- MarketPrice — live crop prices per market

## Endpoints
| Method | URL | Description |
|--------|-----|-------------|
| POST | /agri/farms | Register a farm |
| GET  | /agri/farms | List my farms |
| POST | /agri/crops | Add a crop to a farm |
| GET  | /agri/crops/{farm_id} | List crops on a farm |
| PUT  | /agri/crops/{id}/status | Update crop growth status |
| POST | /agri/logs | Log irrigation / fertilizer activity |
| GET  | /agri/logs/{crop_id} | View all logs for a crop |
| POST | /agri/weather | Log weather data |
| GET  | /agri/weather/{farm_id} | Last 30 weather entries |
| POST | /agri/market-prices | Add market price |
| GET  | /agri/market-prices?crop=wheat | Search prices by crop |

## How to plug into main.py
```python
from extra_starters.agritech.routes import router as agri_router
app.include_router(agri_router, prefix="/agri", tags=["AgriTech"])
```
