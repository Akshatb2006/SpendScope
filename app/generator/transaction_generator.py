from faker import Faker
from datetime import datetime, timedelta
from typing import List, Dict
import random

fake = Faker()

class TransactionGenerator:
    
    CATEGORIES = {
        "groceries": {"merchants": ["Whole Foods", "Safeway", "Trader Joe's"], "amount_range": (-50, -150)},
        "dining": {"merchants": ["Starbucks", "Chipotle", "Panera"], "amount_range": (-15, -50)},
        "transportation": {"merchants": ["Uber", "Lyft", "Shell"], "amount_range": (-10, -80)},
        "utilities": {"merchants": ["PG&E", "Comcast", "AT&T"], "amount_range": (-50, -200)},
        "entertainment": {"merchants": ["Netflix", "Spotify", "AMC"], "amount_range": (-10, -50)},
        "shopping": {"merchants": ["Amazon", "Target", "Walmart"], "amount_range": (-20, -200)},
        "income": {"merchants": ["Employer Direct Deposit"], "amount_range": (2000, 5000)}
    }
    
    @staticmethod
    def generate_transactions(
        account_id: str,
        start_date: datetime,
        days: int = 30,
        daily_count: int = 3
    ) -> List[Dict]:
        transactions = []
        
        for day in range(days):
            txn_date = start_date + timedelta(days=day)
            
            # Generate daily transactions
            for _ in range(random.randint(1, daily_count)):
                category = random.choice(list(TransactionGenerator.CATEGORIES.keys()))
                category_data = TransactionGenerator.CATEGORIES[category]
                
                merchant = random.choice(category_data["merchants"])
                amount_range = category_data["amount_range"]
                amount = round(random.uniform(amount_range[0], amount_range[1]), 2)
                
                transactions.append({
                    "id": f"TXN_{fake.uuid4()[:8]}",
                    "account_id": account_id,
                    "date": txn_date.isoformat(),
                    "amount": amount,
                    "description": f"{merchant} - {category}",
                    "merchant": merchant,
                    "category": category,
                    "status": "posted"
                })

            if day % 15 == 0:
                transactions.append({
                    "id": f"TXN_{fake.uuid4()[:8]}",
                    "account_id": account_id,
                    "date": txn_date.isoformat(),
                    "amount": round(random.uniform(2000, 5000), 2),
                    "description": "Salary Direct Deposit",
                    "merchant": "Employer",
                    "category": "income",
                    "status": "posted"
                })
        
        return transactions