# Theme: Smart Cities

## Likely problem statements
- Citizen issue reporting portal (potholes, broken lights)
- Real-time traffic monitoring system
- Public transport tracker
- Emergency alert broadcasting
- Smart waste management

## Your models (already built)
- CityIssue — category, location, status, upvotes, priority
- TrafficLog — location, congestion 0-100, speed, incidents
- BusStop — name, coordinates, routes
- PublicAlert — type, area, active/expired

## Endpoints
| Method | URL | Description |
|--------|-----|-------------|
| POST | /city/issues | Report a city issue |
| GET  | /city/issues?category=road&status=open | Filter issues |
| PUT  | /city/issues/{id}/status | Update issue status |
| POST | /city/issues/{id}/upvote | Upvote an issue |
| POST | /city/traffic | Log traffic data |
| GET  | /city/traffic?location=MG+Road | Get traffic by location |
| POST | /city/bus-stops | Add a bus stop |
| GET  | /city/bus-stops | All active bus stops |
| POST | /city/alerts | Broadcast public alert |
| GET  | /city/alerts | All active alerts |

## How to plug into main.py
```python
from extra_starters.smartcities.routes import router as city_router
app.include_router(city_router, prefix="/city", tags=["Smart Cities"])
```
