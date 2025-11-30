from abc import ABC, abstractmethod
from typing import Dict, Any
from app.schemas.account_schemas import AccountCreate
from app.schemas.transaction_schemas import TransactionBase

class BaseNormalizer(ABC):
    
    @abstractmethod
    def normalize_account(self, raw_account: Dict[str, Any]) -> AccountCreate:
        pass
    
    @abstractmethod
    def normalize_transaction(self, raw_transaction: Dict[str, Any]) -> TransactionBase:
        pass