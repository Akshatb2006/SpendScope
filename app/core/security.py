from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet
from app.config import get_settings
import base64

settings = get_settings()

ph = PasswordHasher()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False

def get_password_hash(password: str) -> str:
    return ph.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_fernet_key() -> bytes:
    key = settings.ENCRYPTION_KEY.encode()
    return base64.urlsafe_b64encode(key[:32].ljust(32, b'='))

def encrypt_token(token: str) -> str:
    """Encrypt sensitive tokens"""
    f = Fernet(get_fernet_key())
    return f.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    """Decrypt sensitive tokens"""
    f = Fernet(get_fernet_key())
    return f.decrypt(encrypted_token.encode()).decode()
