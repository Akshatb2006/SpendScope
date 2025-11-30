from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.models.account import Account
from app.schemas.transaction_schemas import TransactionResponse, TransactionReconcile, TransactionFilter
from app.services.reconciliation_service import ReconciliationService
from app.services.delta_history_service import DeltaHistoryService
from app.cache import cache

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    account_id: Optional[int] = None,
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
   
    query = db.query(Transaction).join(Account).filter(Account.user_id == current_user.id)
    
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    if category:
        query = query.filter(Transaction.category == category)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    transactions = query.order_by(Transaction.date.desc()).offset(offset).limit(limit).all()
    return transactions

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    transaction = db.query(Transaction).join(Account).filter(
        Transaction.id == transaction_id,
        Account.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transaction

@router.post("/{transaction_id}/reconcile", response_model=TransactionResponse)
def reconcile_transaction(
    transaction_id: int,
    reconcile_data: TransactionReconcile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    transaction = db.query(Transaction).join(Account).filter(
        Transaction.id == transaction_id,
        Account.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    updated = ReconciliationService.reconcile_transaction(
        db, transaction_id, reconcile_data, current_user.id
    )
    
    cache.invalidate_pattern(f"account:{transaction.account_id}:*")
    
    return updated

@router.get("/{transaction_id}/history")
def get_transaction_history(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    transaction = db.query(Transaction).join(Account).filter(
        Transaction.id == transaction_id,
        Account.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    history = DeltaHistoryService.get_transaction_history(db, transaction_id)
    return {"transaction_id": transaction_id, "history": history}