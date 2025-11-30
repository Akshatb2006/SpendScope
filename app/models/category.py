from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
from app.models.custom_types import TZDateTime

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text)
    keywords = Column(Text)  
    merchants = Column(Text)  
    parent_category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(TZDateTime, default=lambda: datetime.now(timezone.utc))
    
    budgets = relationship("Budget", back_populates="category")
    parent = relationship("Category", remote_side=[id], backref="subcategories")