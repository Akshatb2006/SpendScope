from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class TransactionBase(BaseModel):
    date: datetime
    amount: float
    description: str
    merchant: Optional[str] = None
    category: Optional[str] = None

class TransactionCreate(TransactionBase):
    account_id: int
    provider_txn_id: str

class TransactionResponse(TransactionBase):
    id: int
    account_id: int
    provider_txn_id: str
    status: str
    is_duplicate: bool
    is_anomaly: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TransactionReconcile(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = None
    merchant: Optional[str] = None
    reason: str

class TransactionFilter(BaseModel):
    account_id: Optional[int] = None
    category: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None