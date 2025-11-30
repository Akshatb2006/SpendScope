import secrets
from typing import Dict, Optional
from datetime import datetime, timedelta

class OAuthSimulator:
    
    def __init__(self):
        self.auth_codes: Dict[str, dict] = {}
        self.access_tokens: Dict[str, dict] = {}
    
    def generate_auth_code(self, provider_id: str, user_id: int) -> str:
        code = secrets.token_urlsafe(32)
        self.auth_codes[code] = {
            "provider_id": provider_id,
            "user_id": user_id,
            "expires_at": datetime.utcnow() + timedelta(minutes=5)
        }
        return code
    
    def exchange_code(self, code: str) -> Optional[str]:
        auth_data = self.auth_codes.get(code)
        if not auth_data or auth_data["expires_at"] < datetime.utcnow():
            return None
        
        token = secrets.token_urlsafe(64)
        self.access_tokens[token] = {
            "provider_id": auth_data["provider_id"],
            "user_id": auth_data["user_id"],
            "expires_at": datetime.utcnow() + timedelta(days=90)
        }
        del self.auth_codes[code]
        return token
    
    def validate_token(self, token: str) -> Optional[dict]:
        token_data = self.access_tokens.get(token)
        if not token_data or token_data["expires_at"] < datetime.utcnow():
            return None
        return token_data

oauth_sim = OAuthSimulator()