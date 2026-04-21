# Theme: Cyber Security

## Likely problem statements
- Threat detection dashboard
- Password strength auditor
- Vulnerability reporting portal
- Suspicious input scanner (SQLi, XSS)
- Network log analyzer

## Your models (already built)
- ThreatLog — IP, event type, payload, severity
- PasswordAudit — score, feedback
- VulnReport — title, description, severity, status

## Endpoints
| Method | URL | Description |
|--------|-----|-------------|
| POST | /security/log-threat | Log a threat event |
| GET  | /security/threats | View all threats |
| POST | /security/check-password | Score a password 0-100 |
| POST | /security/scan-input | Detect SQLi / XSS in input |
| POST | /security/report-vuln | Submit a vulnerability report |
| GET  | /security/reports | List all reports |

## Built-in utilities (no extra installs needed)
- `score_password()` — scores password strength 0–100 with feedback
- `detect_threats()` — catches SQL injection, XSS, path traversal patterns

## How to plug into main.py
```python
from theme_starters.cybersecurity.routes import router as security_router
app.include_router(security_router, prefix="/security", tags=["Security"])
```
