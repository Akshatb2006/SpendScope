from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.account import Account
from app.schemas.account_schemas import AccountResponse, AccountLink
from app.core.oauth_simulator import oauth_sim
from app.core.security import encrypt_token
from app.providers.provider_registry import provider_registry
from app.cache import cache

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.get("/", response_model=List[AccountResponse])
def list_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cache_key = f"user:{current_user.id}:accounts"
    
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    accounts = db.query(Account).filter(
        Account.user_id == current_user.id,
        Account.is_active == True
    ).all()
    
    cache.set(cache_key, [AccountResponse.from_orm(a).dict() for a in accounts])
    
    return accounts

@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return account

@router.post("/link")
def link_account(
    link_data: AccountLink,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    access_token = oauth_sim.exchange_code(link_data.auth_code)
    if not access_token:
        raise HTTPException(status_code=400, detail="Invalid authorization code")
    
    provider = provider_registry.get_provider(link_data.provider_id)
    
    raw_accounts = provider.fetch_accounts(access_token)
    
    created_accounts = []
    for raw_account in raw_accounts:
        account = Account(
            user_id=current_user.id,
            provider_id=link_data.provider_id,
            provider_account_id=raw_account.get("acct_id") or raw_account.get("account_number") or raw_account.get("id"),
            name=raw_account.get("acct_name") or raw_account.get("nickname") or raw_account.get("display_name"),
            account_type=raw_account.get("acct_type") or raw_account.get("type") or raw_account.get("category"),
            balance=raw_account.get("current_balance") or raw_account.get("balance_amount") or raw_account.get("available"),
            currency=raw_account.get("curr") or raw_account.get("currency_code") or raw_account.get("iso_currency"),
            access_token_encrypted=encrypt_token(access_token)
        )
        db.add(account)
        created_accounts.append(account)
    
    db.commit()
    
    cache.delete(f"user:{current_user.id}:accounts")
    
    return {
        "status": "success",
        "message": f"Linked {len(created_accounts)} accounts",
        "accounts": [{"id": a.id, "name": a.name} for a in created_accounts]
    }
