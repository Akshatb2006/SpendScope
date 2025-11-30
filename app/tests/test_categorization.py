import pytest
from app.services.categorization_service import CategorizationService

def test_categorization():
    """Test transaction categorization"""
    # Test grocery
    category = CategorizationService.categorize("Whole Foods Market", "Whole Foods", -75.50)
    assert category == "groceries"
    
    # Test dining
    category = CategorizationService.categorize("Starbucks Coffee", "Starbucks", -5.50)
    assert category == "dining"
    
    # Test income
    category = CategorizationService.categorize("Salary Deposit", "Employer", 3000.0)
    assert category == "income"