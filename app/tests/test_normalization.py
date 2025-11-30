import pytest
from datetime import datetime
from app.normalization.banka_normalizer import BankANormalizer

def test_banka_account_normalization():
    """Test Bank A account normalization"""
    normalizer = BankANormalizer()
    raw_account = {
        "acct_id": "BA_001",
        "acct_type": "checking",
        "acct_name": "Main Checking",
        "current_balance": 5000.0,
        "curr": "USD"
    }
    
    normalized = normalizer.normalize_account(raw_account)
    assert normalized.provider_id == "banka"
    assert normalized.balance == 5000.0

def test_banka_transaction_normalization():
    """Test Bank A transaction normalization"""
    normalizer = BankANormalizer()
    raw_txn = {
        "txn_id": "BA_TXN_001",
        "txn_date": "2024-01-01T10:00:00",
        "txn_amount": -50.0,
        "txn_desc": "Grocery Store",
        "txn_status": "completed"
    }
    
    normalized = normalizer.normalize_transaction(raw_txn)
    assert normalized.amount == -50.0
    assert "Grocery" in normalized.description
