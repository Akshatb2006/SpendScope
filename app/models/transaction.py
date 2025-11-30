from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Index, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
from app.models.custom_types import TZDateTime

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    provider_txn_id = Column(String, nullable=False)
    date = Column(TZDateTime, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String)
    merchant = Column(String)
    category = Column(String)
    status = Column(String, default="posted")
    hash = Column(String, unique=True, index=True)
    is_duplicate = Column(Boolean, default=False)
    is_anomaly = Column(Boolean, default=False)
    created_at = Column(TZDateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(TZDateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    account = relationship("Account", back_populates="transactions")
    audit_logs = relationship("AuditLog", back_populates="transaction", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_account_date', 'account_id', 'date'),
        Index('idx_category_date', 'category', 'date'),
    )