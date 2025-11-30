from sqlalchemy.orm import Session
from app.models.user import User
from app.models.category import Category
from app.core.security import get_password_hash
from app.generator.account_generator import AccountGenerator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SeedData:
    
    @staticmethod
    def seed_categories(db: Session):
        default_categories = [
            "groceries", "dining", "transportation", "utilities",
            "entertainment", "shopping", "healthcare", "income", "other"
        ]
        
        for cat_name in default_categories:
            existing = db.query(Category).filter(Category.name == cat_name).first()
            if not existing:
                category = Category(
                    name=cat_name,
                    description=f"Default category: {cat_name}"
                )
                db.add(category)
        
        db.commit()
        logger.info("Categories seeded")
    
    @staticmethod
    def seed_test_user(db: Session) -> User:
        email = "test@example.com"
        existing = db.query(User).filter(User.email == email).first()
        
        if existing:
            return existing
        
        user = User(
            email=email,
            full_name="Test User",
            hashed_password=get_password_hash("password123")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"Test user created: {email}")
        return user
