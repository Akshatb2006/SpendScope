from typing import Dict
from app.providers.base_provider import BaseProvider
from app.providers.banka_provider import BankAProvider
from app.providers.bankb_provider import BankBProvider
from app.providers.bankc_provider import BankCProvider
from typing import List, Dict


class ProviderRegistry:
    
    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {
            "banka": BankAProvider(),
            "bankb": BankBProvider(),
            "bankc": BankCProvider()
        }
    
    def get_provider(self, provider_id: str) -> BaseProvider:
        provider = self._providers.get(provider_id)
        if not provider:
            raise ValueError(f"Unknown provider: {provider_id}")
        return provider
    
    def list_providers(self) -> List[Dict[str, str]]:
        return [
            {
                "id": pid,
                "name": provider.get_provider_name()
            }
            for pid, provider in self._providers.items()
        ]

provider_registry = ProviderRegistry()