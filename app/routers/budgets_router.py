from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.budget import Budget
from app.schemas.budget_schemas import BudgetCreate, BudgetUpdate, BudgetResponse
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/budgets", tags=["Budgets"])

@router.post("/", response_model=BudgetResponse)
def create_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budget = BudgetService.create_budget(
        db, current_user.id, budget_data.category_name, 
        budget_data.amount, budget_data.period
    )
    
    return BudgetResponse(
        id=budget.id,
        category_name=budget.category_name,
        amount=budget.amount,
        period=budget.period.value,
        current_spend=budget.current_spend,
        percentage_used=0.0,
        alert_sent=False
    )

@router.get("/", response_model=List[BudgetResponse])
def list_budgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    statuses = BudgetService.get_budget_status(db, current_user.id)
    return [BudgetResponse(**s) for s in statuses]

@router.delete("/{budget_id}")
def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    db.delete(budget)
    db.commit()
    return {"status": "success"}
