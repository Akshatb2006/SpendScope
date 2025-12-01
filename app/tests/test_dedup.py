import pytest
from datetime import datetime
from app.core.hashing import generate_transaction_hash

def test_transaction_hash():
    date = datetime(2024, 1, 1)
    hash1 = generate_transaction_hash(date, -50.0, "Grocery Store", "banka")
    hash2 = generate_transaction_hash(date, -50.0, "Grocery Store", "banka")
    hash3 = generate_transaction_hash(date, -50.0, "Different Store", "banka")
    
    assert hash1 == hash2  
    assert hash1 != hash3 