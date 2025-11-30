from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.account import Account
from app.services.sync_service import SyncService

router = APIRouter(prefix="/sync", tags=["Sync"])

@router.post("/account/{account_id}")
def sync_account(
    account_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    background_tasks.add_task(SyncService.sync_account, db, account_id)
    
    return {"status": "sync_initiated", "account_id": account_id}

@router.get("/logs/account/{account_id}")
def get_sync_logs(
    account_id: int,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    from app.models.sync_cursor import SyncCursor
    
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    logs = db.query(SyncCursor).filter(
        SyncCursor.account_id == account_id
    ).order_by(SyncCursor.created_at.desc()).limit(limit).all()
    
    return {"account_id": account_id, "logs": logs}
