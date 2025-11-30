from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.transaction import Transaction
from datetime import datetime, timedelta, timezone
from typing import List, Dict
import statistics
import logging

logger = logging.getLogger(__name__)

class AnomalyService:
    @staticmethod
    def detect_anomalies(db: Session, account_id: int, days_lookback: int = 90) -> List[Dict]:
        """Detect transaction anomalies using heuristics"""
        anomalies = []
        
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_lookback)
            transactions = db.query(Transaction).filter(
                Transaction.account_id == account_id,
                Transaction.date >= cutoff_date
            ).all()
            
            if len(transactions) < 10:
                return []  
            
            category_amounts = {}
            for txn in transactions:
                if txn.category not in category_amounts:
                    category_amounts[txn.category] = []
                category_amounts[txn.category].append(abs(txn.amount))
            
            recent_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
            recent_txns = [t for t in transactions if t.date >= recent_cutoff]
            
            for txn in recent_txns:
                category = txn.category
                amount = abs(txn.amount)
                
                if category not in category_amounts or len(category_amounts[category]) < 5:
                    continue
                
                historical = category_amounts[category]
                mean = statistics.mean(historical)
                
                try:
                    stdev = statistics.stdev(historical)
                except:
                    continue
                
                if stdev == 0:
                    continue
                
                z_score = (amount - mean) / stdev
                
                if abs(z_score) > 2:
                    severity = "high" if abs(z_score) > 3 else "medium"
                    anomalies.append({
                        "transaction_id": txn.id,
                        "type": "unusual_amount",
                        "description": f"${amount:.2f} is {abs(z_score):.1f}σ from normal ${mean:.2f} for {category}",
                        "severity": severity,
                        "z_score": z_score,
                        "date": txn.date.isoformat()
                    })
                    
                    txn.is_anomaly = True
            
            merchant_history = set([t.merchant for t in transactions if t.date < recent_cutoff])
            for txn in recent_txns:
                if txn.merchant and txn.merchant not in merchant_history:
                    anomalies.append({
                        "transaction_id": txn.id,
                        "type": "new_merchant",
                        "description": f"First transaction with merchant: {txn.merchant}",
                        "severity": "low",
                        "date": txn.date.isoformat()
                    })
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
        
        return anomalies