from typing import Dict, Any
from datetime import datetime
from app.normalization.base_normalizer import BaseNormalizer
from app.schemas.account_schemas import AccountCreate
from app.schemas.transaction_schemas import TransactionBase

class BankANormalizer(BaseNormalizer):
    def normalize_account(self, raw: Dict[str, Any]) -> AccountCreate:
        return AccountCreate(
            provider_id="banka",
            provider_account_id=raw["acct_id"],
            name=raw["acct_name"],
            account_type=raw["acct_type"],
            balance=raw["current_balance"],
            currency=raw["curr"]
        )
    
    def normalize_transaction(self, raw: Dict[str, Any]) -> TransactionBase:
        return TransactionBase(
            date=datetime.fromisoformat(raw["txn_date"]),
            amount=raw["txn_amount"],
            description=raw["txn_desc"],
            merchant=raw.get("merchant_info"),
            category=None
        )