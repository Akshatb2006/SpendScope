from typing import Dict, Any
from datetime import datetime
from app.normalization.base_normalizer import BaseNormalizer
from app.schemas.account_schemas import AccountCreate
from app.schemas.transaction_schemas import TransactionBase

class BankBNormalizer(BaseNormalizer):
    def normalize_account(self, raw: Dict[str, Any]) -> AccountCreate:
        return AccountCreate(
            provider_id="bankb",
            provider_account_id=raw["account_number"],
            name=raw["nickname"],
            account_type=raw["type"],
            balance=raw["balance_amount"],
            currency=raw["currency_code"]
        )
    
    def normalize_transaction(self, raw: Dict[str, Any]) -> TransactionBase:
        return TransactionBase(
            date=datetime.fromisoformat(raw["date"]),
            amount=raw["amt"],
            description=raw["memo"],
            merchant=raw.get("merchant_name"),
            category=None
        )
