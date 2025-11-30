from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Personal Finance Aggregator"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    
    DATABASE_URL: str
    
    REDIS_URL: str
    CACHE_TTL: int = 300
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENCRYPTION_KEY: str
    
    SYNC_INTERVAL_MINUTES: int = 15
    SYNC_TIMEOUT_SECONDS: int = 30
    
    MAX_WORKERS: int = 4
    API_LATENCY_TARGET_MS: int = 150
    ALERT_LATENCY_TARGET_SECONDS: int = 60
    
    model_config = SettingsConfigDict(env_file=".env")

@lru_cache()
def get_settings() -> Settings:
    return Settings()