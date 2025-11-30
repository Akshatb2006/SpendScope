from datetime import datetime
from app.core.hashing import generate_transaction_hash

def create_transaction_hash(
    date: datetime,
    amount: float,
    description: str,
    provider_id: str
) -> str:
    return generate_transaction_hash(date, amount, description, provider_id)