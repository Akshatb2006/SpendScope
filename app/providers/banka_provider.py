from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.providers.base_provider import BaseProvider
import random

class BankAProvider(BaseProvider):
    
    def get_provider_id(self) -> str:
        return "banka"
    
    def get_provider_name(self) -> str:
        return "Bank of America Mock"
    
    def fetch_accounts(self, token: str) -> List[Dict[str, Any]]:
        return [
            {
                "acct_id": "BA_CHK_001",
                "acct_type": "checking",
                "acct_name": "Premier Checking",
                "current_balance": 5420.50,
                "curr": "USD",
                "status": "active"
            },
            {
                "acct_id": "BA_SAV_002",
                "acct_type": "savings",
                "acct_name": "High Yield Savings",
                "current_balance": 12000.00,
                "curr": "USD",
                "status": "active"
            }
        ]
    
    def fetch_transactions(
        self,
        token: str,
        account_id: str,
        since_date: datetime = None
    ) -> List[Dict[str, Any]]:
        base_date = since_date or datetime.utcnow() - timedelta(days=30)
        transactions = []
        
        merchants = ["Whole Foods", "Shell Gas", "Starbucks", "Amazon", "Walmart"]
        for i in range(15):
            transactions.append({
                "txn_id": f"BA_TXN_{random.randint(10000, 99999)}",
                "txn_date": (base_date + timedelta(days=i)).isoformat(),
                "txn_amount": round(random.uniform(-200, 50), 2),
                "txn_desc": random.choice(merchants),
                "txn_status": "completed",
                "merchant_info": random.choice(merchants)
            })
        
        return transactions
