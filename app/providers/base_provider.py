from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime

class BaseProvider(ABC):
    
    @abstractmethod
    def get_provider_id(self) -> str:
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        pass
    
    @abstractmethod
    def fetch_accounts(self, token: str) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def fetch_transactions(
        self,
        token: str,
        account_id: str,
        since_date: datetime = None
    ) -> List[Dict[str, Any]]:
        pass
    
    def validate_token(self, token: str) -> bool:
        return True  