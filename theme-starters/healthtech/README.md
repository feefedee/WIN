# Theme: Health Tech

## Likely problem statements
- Remote patient monitoring system
- Symptom checker / triage app
- Appointment booking for rural areas
- Personal health record manager
- Emergency alert system

## Your models (already built)
- Patient — profile with age, blood type, conditions
- HealthRecord — vitals, severity, notes
- Appointment — doctor, specialty, scheduled time

## Endpoints
| Method | URL | Description |
|--------|-----|-------------|
| POST | /patient | Create patient profile |
| POST | /records/{patient_id} | Log a health record |
| GET  | /records/{patient_id} | View all records |
| POST | /appointments | Book appointment |
| GET  | /appointments | View my appointments |

## Extra pip installs you may need
```
pip install openai  # if adding AI symptom analysis
pip install twilio  # if adding SMS alerts
```

## Quick AI add-on (symptom checker)
```python
import openai

def analyze_symptoms(symptoms: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"Patient reports: {symptoms}. Give a brief triage suggestion."
        }]
    )
    return response.choices[0].message.content
```

## How to plug into main.py
```python
from theme_starters.healthtech.routes import router as health_router
app.include_router(health_router, prefix="/health", tags=["Health"])
```
