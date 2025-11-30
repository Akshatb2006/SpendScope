from sqlalchemy.orm import Session
from app.models.budget import Budget, BudgetPeriod
from app.services.alert_service import AlertService
from datetime import datetime, timedelta, timezone
from typing import List
import logging

logger = logging.getLogger(__name__)

class BudgetService:
    @staticmethod
    def create_budget(db: Session, user_id: int, category_name: str, amount: float, period: str) -> Budget:
        budget = Budget(
            user_id=user_id,
            category_name=category_name,
            amount=amount,
            period=BudgetPeriod(period),
            period_start=datetime.now(timezone.utc)
        )
        db.add(budget)
        db.commit()
        db.refresh(budget)
        return budget
    
    @staticmethod
    def update_budget_spending(db: Session, user_id: int, category: str, transaction_amount: float):
        try:
            budget = db.query(Budget).filter(
                Budget.user_id == user_id,
                Budget.category_name == category
            ).first()
            
            if not budget:
                return
            
            BudgetService.reset_budget_if_needed(db, budget)
            
            if transaction_amount < 0:
                budget.current_spend += abs(transaction_amount)
                db.commit()
                
                percentage = (budget.current_spend / budget.amount) * 100
                if percentage >= 100 and not budget.alert_sent:
                    AlertService.send_budget_alert(user_id, category, budget, "exceeded")
                    budget.alert_sent = True
                    db.commit()
                elif percentage >= 80 and percentage < 100 and not budget.alert_sent:
                    AlertService.send_budget_alert(user_id, category, budget, "warning")
        except Exception as e:
            logger.error(f"Budget update error: {e}")
            db.rollback()
    
    @staticmethod
    def reset_budget_if_needed(db: Session, budget: Budget):
        now = datetime.now(timezone.utc)
        days_elapsed = (now - budget.period_start).days
        
        should_reset = False
        if budget.period == BudgetPeriod.WEEKLY and days_elapsed >= 7:
            should_reset = True
        elif budget.period == BudgetPeriod.MONTHLY and days_elapsed >= 30:
            should_reset = True
        
        if should_reset:
            budget.current_spend = 0.0
            budget.alert_sent = False
            budget.period_start = now
            db.commit()
    
    @staticmethod
    def get_budget_status(db: Session, user_id: int) -> List[dict]:
        budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
        return [
            {
                "id": b.id,
                "category_name": b.category_name,
                "amount": b.amount,
                "current_spend": b.current_spend,
                "percentage_used": (b.current_spend / b.amount * 100) if b.amount > 0 else 0,
                "remaining": b.amount - b.current_spend,
                "period": b.period.value,
                "alert_sent": b.alert_sent
            }
            for b in budgets
        ]