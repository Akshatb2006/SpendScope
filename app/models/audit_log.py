from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
from app.models.custom_types import TZDateTime

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)  
    field_changed = Column(String)
    old_value = Column(Text)
    new_value = Column(Text)
    changed_by = Column(String)  
    reason = Column(Text)
    metainfo = Column(JSON)
    created_at = Column(TZDateTime, default=lambda: datetime.now(timezone.utc))
    
    transaction = relationship("Transaction", back_populates="audit_logs")