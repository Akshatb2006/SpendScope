import pytest
from datetime import datetime, timedelta, timezone
from fastapi import status
from app.services.budget_service import BudgetService
from app.models.budget import Budget, BudgetPeriod

class TestBudgetService:
    
    def test_create_budget(self, db_session, test_user):
        budget = BudgetService.create_budget(
            db_session, test_user.id, "groceries", 500.00, "monthly"
        )
        
        assert budget.id is not None
        assert budget.user_id == test_user.id
        assert budget.category_name == "groceries"
        assert budget.amount == 500.00
        assert budget.period == BudgetPeriod.MONTHLY
        assert budget.current_spend == 0.0
    
    def test_update_budget_spending(self, db_session, test_user):
        budget = BudgetService.create_budget(
            db_session, test_user.id, "dining", 300.00, "monthly"
        )
        
        BudgetService.update_budget_spending(db_session, test_user.id, "dining", -50.00)
        db_session.refresh(budget)
        
        assert budget.current_spend == 50.00
        
        BudgetService.update_budget_spending(db_session, test_user.id, "dining", -75.00)
        db_session.refresh(budget)
        
        assert budget.current_spend == 125.00
    
    def test_budget_alert_threshold(self, db_session, test_user):
        budget = BudgetService.create_budget(
            db_session, test_user.id, "entertainment", 100.00, "monthly"
        )
        
        BudgetService.update_budget_spending(db_session, test_user.id, "entertainment", -110.00)
        db_session.refresh(budget)
        
        assert budget.current_spend >= budget.amount
        assert budget.alert_sent is True
    
    def test_reset_weekly_budget(self, db_session, test_user):
        budget = Budget(
            user_id=test_user.id,
            category_name="groceries",
            amount=200.00,
            period=BudgetPeriod.WEEKLY,
            current_spend=150.00,
            period_start=datetime.now(timezone.utc) - timedelta(days=8)  
        )
        db_session.add(budget)
        db_session.commit()
        
        BudgetService.reset_budget_if_needed(db_session, budget)
        db_session.refresh(budget)
        
        assert budget.current_spend == 0.0
        assert budget.alert_sent is False
    
    def test_reset_monthly_budget(self, db_session, test_user):
        budget = Budget(
            user_id=test_user.id,
            category_name="dining",
            amount=500.00,
            period=BudgetPeriod.MONTHLY,
            current_spend=400.00,
            period_start=datetime.now(timezone.utc) - timedelta(days=31)  
        )
        db_session.add(budget)
        db_session.commit()
        
        BudgetService.reset_budget_if_needed(db_session, budget)
        db_session.refresh(budget)
        
        assert budget.current_spend == 0.0
    
    def test_get_budget_status(self, db_session, test_user):
        BudgetService.create_budget(db_session, test_user.id, "groceries", 500.00, "monthly")
        BudgetService.create_budget(db_session, test_user.id, "dining", 300.00, "monthly")
        
        BudgetService.update_budget_spending(db_session, test_user.id, "groceries", -200.00)
        BudgetService.update_budget_spending(db_session, test_user.id, "dining", -150.00)
        
        status = BudgetService.get_budget_status(db_session, test_user.id)
        
        assert len(status) == 2
        assert status[0]["category_name"] in ["groceries", "dining"]
        assert status[0]["percentage_used"] > 0

class TestBudgetEndpoints:
    
    def test_create_budget_endpoint(self, client, auth_headers):
        response = client.post(
            "/budgets/",
            headers=auth_headers,
            json={
                "category_name": "groceries",
                "amount": 500.00,
                "period": "monthly"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["category_name"] == "groceries"
        assert data["amount"] == 500.00
    
    def test_list_budgets(self, client, auth_headers, db_session, test_user):
        BudgetService.create_budget(db_session, test_user.id, "groceries", 500.00, "monthly")
        BudgetService.create_budget(db_session, test_user.id, "dining", 300.00, "weekly")
        
        response = client.get("/budgets/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 2
    
    def test_delete_budget(self, client, auth_headers, db_session, test_user):
        budget = BudgetService.create_budget(
            db_session, test_user.id, "entertainment", 200.00, "monthly"
        )
        
        response = client.delete(f"/budgets/{budget.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        deleted = db_session.query(Budget).filter(Budget.id == budget.id).first()
        assert deleted is None
