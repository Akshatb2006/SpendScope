from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class BudgetCreate(BaseModel):
    category_name: str
    amount: float = Field(gt=0)
    period: str = "monthly"

class BudgetUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    period: Optional[str] = None

class BudgetResponse(BaseModel):
    id: int
    category_name: str
    amount: float
    period: str
    current_spend: float
    percentage_used: float
    alert_sent: bool
    
    model_config = ConfigDict(from_attributes=True)