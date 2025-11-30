import hashlib
from datetime import datetime

def generate_transaction_hash(
    date: datetime,
    amount: float,
    description: str,
    provider_id: str
) -> str:
    """Generate SHA256 hash for transaction deduplication"""
    content = f"{date.isoformat()}|{amount}|{description}|{provider_id}"
    return hashlib.sha256(content.encode()).hexdigest()