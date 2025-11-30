from app.cache import cache
from app.models.budget import Budget
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class AlertService:
    @staticmethod
    def send_budget_alert(user_id: int, category: str, budget: Budget, alert_type: str):
        try:
            percentage = (budget.current_spend / budget.amount) * 100
            
            alert_data = {
                "type": "budget_alert",
                "alert_type": alert_type,  
                "user_id": user_id,
                "category": category,
                "budget_amount": budget.amount,
                "current_spend": budget.current_spend,
                "percentage": round(percentage, 2),
                "remaining": budget.amount - budget.current_spend,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            cache.publish("alerts", alert_data)
            logger.info(f"Budget alert sent for user {user_id}, category {category}")
            
        except Exception as e:
            logger.error(f"Alert sending error: {e}")
    
    @staticmethod
    def send_anomaly_alert(user_id: int, transaction_id: int, anomaly: dict):
        try:
            alert_data = {
                "type": "anomaly_alert",
                "user_id": user_id,
                "transaction_id": transaction_id,
                "anomaly_type": anomaly["type"],
                "description": anomaly["description"],
                "severity": anomaly["severity"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            cache.publish("alerts", alert_data)
            logger.info(f"Anomaly alert sent for transaction {transaction_id}")
            
        except Exception as e:
            logger.error(f"Anomaly alert error: {e}")