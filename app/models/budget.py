from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
from app.models.custom_types import TZDateTime
import enum

class BudgetPeriod(enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    period = Column(Enum(BudgetPeriod), default=BudgetPeriod.MONTHLY)
    current_spend = Column(Float, default=0.0)
    alert_sent = Column(Boolean, default=False)
    period_start = Column(TZDateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(TZDateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(TZDateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")