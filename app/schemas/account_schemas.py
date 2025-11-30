from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class AccountBase(BaseModel):
    name: str
    account_type: str
    balance: float
    currency: str = "USD"

class AccountCreate(AccountBase):
    provider_id: str
    provider_account_id: str

class AccountResponse(AccountBase):
    id: int
    provider_id: str
    last_synced: Optional[datetime]
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AccountLink(BaseModel):
    provider_id: str
    auth_code: str