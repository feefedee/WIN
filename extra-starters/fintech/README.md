# Theme: FinTech

## Likely problem statements
- Digital wallet with P2P transfers
- Fraud detection system
- Loan eligibility & EMI calculator
- Expense tracker with categories
- Micro-lending platform

## Your models (already built)
- Wallet — balance, currency, active status
- Transaction — type, amount, category, fraud_score, status
- FraudAlert — reason, score, reviewed flag
- Loan — amount, interest rate, tenure, auto-calculated EMI

## Endpoints
| Method | URL | Description |
|--------|-----|-------------|
| POST | /fin/wallet/create | Create a wallet |
| GET  | /fin/wallet | Get my balance |
| POST | /fin/wallet/topup | Add money to wallet |
| POST | /fin/transfer | Send money (auto fraud check) |
| GET  | /fin/transactions | My transaction history |
| GET  | /fin/fraud-alerts | View flagged transactions |
| POST | /fin/loans/apply | Apply for loan + get EMI |

## Built-in fraud detection (no ML needed)
Automatically flags transactions scoring ≥ 50:
- Large amount (>₹50,000) → +40 points
- High frequency (>5 txns/hour) → +35 points
- Round number (multiples of ₹1000) → +10 points

## How to plug into main.py
```python
from extra_starters.fintech.routes import router as fin_router
app.include_router(fin_router, prefix="/fin", tags=["FinTech"])
```
