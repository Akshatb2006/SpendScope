from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.providers.base_provider import BaseProvider
import random

class BankBProvider(BaseProvider):
    
    def get_provider_id(self) -> str:
        return "bankb"
    
    def get_provider_name(self) -> str:
        return "Chase Mock"
    
    def fetch_accounts(self, token: str) -> List[Dict[str, Any]]:
        return [
            {
                "account_number": "BB_CC_001",
                "type": "credit",
                "nickname": "Freedom Unlimited",
                "balance_amount": -1250.75,
                "currency_code": "USD",
                "account_status": "ACTIVE"
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
        
        vendors = ["Netflix", "Uber Eats", "Target", "CVS Pharmacy", "AT&T"]
        for i in range(12):
            transactions.append({
                "id": f"BB_{random.randint(1000, 9999)}",
                "date": (base_date + timedelta(days=i*2)).isoformat(),
                "amt": round(random.uniform(-150, 10), 2),
                "memo": random.choice(vendors),
                "merchant_name": random.choice(vendors),
                "state": "posted",
                "type": "purchase"
            })
        
        return transactions