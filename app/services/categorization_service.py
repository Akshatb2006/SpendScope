import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class CategorizationService:
    RULES = {
        "groceries": {
            "keywords": ["grocery", "supermarket", "whole foods", "trader joe", "safeway", "kroger"],
            "merchants": ["walmart", "target", "costco", "albertsons"]
        },
        "dining": {
            "keywords": ["restaurant", "cafe", "coffee", "pizza", "burger", "food"],
            "merchants": ["starbucks", "mcdonald", "subway", "chipotle", "panera"]
        },
        "transportation": {
            "keywords": ["uber", "lyft", "gas", "fuel", "parking", "toll", "transit"],
            "merchants": ["shell", "chevron", "exxon", "bp", "uber"]
        },
        "utilities": {
            "keywords": ["electric", "water", "internet", "phone", "cable", "utility"],
            "merchants": ["comcast", "at&t", "verizon", "pg&e"]
        },
        "entertainment": {
            "keywords": ["netflix", "spotify", "hulu", "movie", "theater", "concert"],
            "merchants": ["netflix", "spotify", "apple music", "amazon prime"]
        },
        "shopping": {
            "keywords": ["amazon", "ebay", "online", "retail"],
            "merchants": ["amazon", "ebay", "walmart.com"]
        },
        "healthcare": {
            "keywords": ["pharmacy", "medical", "doctor", "hospital", "dental"],
            "merchants": ["cvs", "walgreens", "rite aid"]
        },
        "income": {
            "keywords": ["salary", "payroll", "deposit", "payment received", "direct deposit"],
            "amount_threshold": 500
        }
    }
    
    @staticmethod
    def categorize(description: str, merchant: Optional[str], amount: float) -> str:
        """Categorize transaction based on rules"""
        try:
            desc_lower = description.lower()
            merchant_lower = (merchant or "").lower()
            
            if amount > 0:
                for keyword in CategorizationService.RULES["income"]["keywords"]:
                    if keyword in desc_lower:
                        return "income"
                if amount >= CategorizationService.RULES["income"]["amount_threshold"]:
                    return "income"
            
            for category, rules in CategorizationService.RULES.items():
                if category == "income":
                    continue
                
                for keyword in rules.get("keywords", []):
                    if keyword in desc_lower or keyword in merchant_lower:
                        return category
                
                for merchant_pattern in rules.get("merchants", []):
                    if merchant_pattern in merchant_lower:
                        return category
            
            return "other"
        except Exception as e:
            logger.error(f"Categorization error: {e}")
            return "other"
    
    @staticmethod
    def apply_user_rule(description: str, merchant: Optional[str], user_category: str) -> str:
        return user_category
