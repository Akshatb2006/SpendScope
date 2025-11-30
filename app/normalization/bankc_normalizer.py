from typing import Dict, Any
from datetime import datetime
from app.normalization.base_normalizer import BaseNormalizer
from app.schemas.account_schemas import AccountCreate
from app.schemas.transaction_schemas import TransactionBase

class BankCNormalizer(BaseNormalizer):
    def normalize_account(self, raw: Dict[str, Any]) -> AccountCreate:
        return AccountCreate(
            provider_id="bankc",
            provider_account_id=raw["id"],
            name=raw["display_name"],
            account_type=raw["category"],
            balance=raw["available"],
            currency=raw["iso_currency"]
        )
    
    def normalize_transaction(self, raw: Dict[str, Any]) -> TransactionBase:
        return TransactionBase(
            date=datetime.fromisoformat(raw["posted_date"]),
            amount=raw["transaction_amount"],
            description=raw["description"],
            merchant=raw.get("vendor"),
            category=None
        )
    