from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.account import Account
from app.services.anomaly_service import AnomalyService

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])

@router.get("/account/{account_id}")
def detect_account_anomalies(
    account_id: int,
    days_lookback: int = 90,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    anomalies = AnomalyService.detect_anomalies(db, account_id, days_lookback)
    return {"account_id": account_id, "anomalies": anomalies}