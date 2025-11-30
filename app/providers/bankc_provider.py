from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.providers.base_provider import BaseProvider
import random

class BankCProvider(BaseProvider):
    
    def get_provider_id(self) -> str:
        return "bankc"
    
    def get_provider_name(self) -> str:
        return "Fidelity Investment Mock"
    
    def fetch_accounts(self, token: str) -> List[Dict[str, Any]]:
        return [
            {
                "id": "BC_BROK_999",
                "category": "investment",
                "display_name": "Individual Brokerage",
                "available": 45000.00,
                "iso_currency": "USD",
                "is_active": True
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
        
        actions = ["Stock Buy - AAPL", "Dividend - MSFT", "Bond Purchase", "ETF Buy - SPY"]
        for i in range(8):
            transactions.append({
                "transaction_id": f"BC_T{random.randint(100, 999)}",
                "posted_date": (base_date + timedelta(days=i*3)).isoformat(),
                "transaction_amount": round(random.uniform(-2000, 500), 2),
                "description": random.choice(actions),
                "vendor": "Fidelity Investments",
                "status_code": "COMPLETE",
                "transaction_type": "investment"
            })
        
        return transactions