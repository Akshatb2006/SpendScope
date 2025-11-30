from faker import Faker
from typing import List, Dict
import random

fake = Faker()

class AccountGenerator:
    
    ACCOUNT_TYPES = ["checking", "savings", "credit", "investment"]
    
    @staticmethod
    def generate_accounts(count: int = 3) -> List[Dict]:
        accounts = []
        
        for i in range(count):
            account_type = random.choice(AccountGenerator.ACCOUNT_TYPES)
            
            if account_type == "credit":
                balance = round(random.uniform(-5000, -100), 2)
            elif account_type == "investment":
                balance = round(random.uniform(10000, 100000), 2)
            else:
                balance = round(random.uniform(500, 20000), 2)
            
            accounts.append({
                "id": f"ACC_{i:04d}",
                "type": account_type,
                "name": f"{account_type.capitalize()} Account",
                "balance": balance,
                "currency": "USD"
            })
        
        return accounts
