from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Text
from datetime import datetime, timezone
from app.database import Base
from app.models.custom_types import TZDateTime

class SyncCursor(Base):
    __tablename__ = "sync_cursors"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    provider_id = Column(String, nullable=False)
    cursor_value = Column(String)
    last_sync_date = Column(TZDateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String) 
    records_fetched = Column(Integer, default=0)
    records_inserted = Column(Integer, default=0)
    records_deduplicated = Column(Integer, default=0)
    duration_seconds = Column(Float)
    error_message = Column(Text)
    meta_info = Column(JSON)
    created_at = Column(TZDateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(TZDateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))