import pytest
from datetime import datetime, timedelta, timezone
from app.generator.account_generator import AccountGenerator
from app.generator.transaction_generator import TransactionGenerator
from app.generator.anomaly_generator import AnomalyGenerator
from app.generator.seed_data import SeedData

class TestAccountGenerator:
    """Test account generator"""
    
    def test_generate_accounts(self):
        """Test generating multiple accounts"""
        accounts = AccountGenerator.generate_accounts(count=5)
        
        assert len(accounts) == 5
        assert all("id" in acc for acc in accounts)
        assert all("type" in acc for acc in accounts)
        assert all("balance" in acc for acc in accounts)
    
    def test_account_types(self):
        """Test different account types are generated"""
        accounts = AccountGenerator.generate_accounts(count=20)
        types = set(acc["type"] for acc in accounts)
        
        # Should have multiple types
        assert len(types) > 1
        assert types.issubset({"checking", "savings", "credit", "investment"})
    
    def test_credit_accounts_negative_balance(self):
        """Test credit accounts have negative balances"""
        accounts = AccountGenerator.generate_accounts(count=50)
        credit_accounts = [acc for acc in accounts if acc["type"] == "credit"]
        
        if credit_accounts:  # If any credit accounts generated
            assert all(acc["balance"] < 0 for acc in credit_accounts)
    
    def test_account_unique_ids(self):
        """Test that account IDs are unique"""
        accounts = AccountGenerator.generate_accounts(count=10)
        ids = [acc["id"] for acc in accounts]
        
        assert len(ids) == len(set(ids))  # All unique

class TestTransactionGenerator:
    """Test transaction generator"""
    
    def test_generate_transactions(self):
        """Test generating transactions"""
        start_date = datetime(2024, 1, 1)
        transactions = TransactionGenerator.generate_transactions(
            account_id="ACC_001",
            start_date=start_date,
            days=30,
            daily_count=3
        )
        
        assert len(transactions) > 30  # At least daily transactions + income
        assert all("id" in txn for txn in transactions)
        assert all("amount" in txn for txn in transactions)
        assert all("category" in txn for txn in transactions)
    
    def test_transaction_date_range(self):
        """Test transactions span correct date range"""
        start_date = datetime(2024, 1, 1)
        transactions = TransactionGenerator.generate_transactions(
            account_id="ACC_001",
            start_date=start_date,
            days=30
        )
        
        dates = [datetime.fromisoformat(txn["date"]) for txn in transactions]
        min_date = min(dates)
        max_date = max(dates)
        
        assert min_date >= start_date
        assert max_date <= start_date + timedelta(days=30)
    
    def test_transaction_categories(self):
        """Test various categories are generated"""
        transactions = TransactionGenerator.generate_transactions(
            account_id="ACC_001",
            start_date=datetime.now(timezone.utc),
            days=30,
            daily_count=5
        )
        
        categories = set(txn["category"] for txn in transactions)
        
        # Should have multiple categories
        assert len(categories) > 1
        assert "income" in categories
    
    def test_income_transactions(self):
        """Test income transactions are generated"""
        transactions = TransactionGenerator.generate_transactions(
            account_id="ACC_001",
            start_date=datetime.now(timezone.utc),
            days=30
        )
        
        income_txns = [txn for txn in transactions if txn["category"] == "income"]
        
        # Should have at least 2 income transactions (day 0 and 15)
        assert len(income_txns) >= 2
        assert all(txn["amount"] > 0 for txn in income_txns)
    
    def test_expense_transactions_negative(self):
        """Test expense transactions have negative amounts"""
        transactions = TransactionGenerator.generate_transactions(
            account_id="ACC_001",
            start_date=datetime.now(timezone.utc),
            days=10
        )
        
        expenses = [txn for txn in transactions if txn["category"] != "income"]
        
        assert all(txn["amount"] < 0 for txn in expenses)

class TestAnomalyGenerator:
    """Test anomaly generator"""
    
    def test_inject_anomalies(self):
        """Test injecting anomalies into transactions"""
        # Generate normal transactions
        transactions = TransactionGenerator.generate_transactions(
            account_id="ACC_001",
            start_date=datetime.now(timezone.utc),
            days=10
        )
        original_count = len(transactions)
        
        # Inject anomalies
        transactions_with_anomalies = AnomalyGenerator.inject_anomalies(
            transactions, anomaly_rate=0.1
        )
        
        # Count should increase (due to duplicates) or stay same
        assert len(transactions_with_anomalies) >= original_count
    
    def test_anomaly_rate(self):
        """Test anomaly injection rate"""
        transactions = TransactionGenerator.generate_transactions(
            account_id="ACC_001",
            start_date=datetime.now(timezone.utc),
            days=30
        )
        original_count = len(transactions)
        
        # Inject 20% anomalies
        transactions_with_anomalies = AnomalyGenerator.inject_anomalies(
            transactions, anomaly_rate=0.2
        )
        
        # Check for anomaly markers
        anomalies = [t for t in transactions_with_anomalies if "[ANOMALY]" in t.get("description", "")]
        suspicious = [t for t in transactions_with_anomalies if "Suspicious" in t.get("description", "")]
        
        # Should have some anomalies
        assert len(anomalies) > 0 or len(suspicious) > 0
    
    def test_high_amount_anomaly(self):
        """Test high amount anomaly injection"""
        transactions = [
            {
                "id": "TXN_001",
                "account_id": "ACC_001",
                "date": datetime.now(timezone.utc).isoformat(),
                "amount": -50.00,
                "description": "Normal Transaction",
                "merchant": "Store",
                "category": "groceries"
            }
        ]
        
        # Inject anomalies multiple times to increase chance of high_amount
        for _ in range(10):
            transactions_copy = transactions.copy()
            result = AnomalyGenerator.inject_anomalies(transactions_copy, anomaly_rate=1.0)
            
            # Check if amount was multiplied
            modified = [t for t in result if abs(t["amount"]) > 100]
            if modified:
                assert any("[ANOMALY]" in t["description"] for t in modified)
                break

class TestSeedData:
    """Test database seeding"""
    
    def test_seed_categories(self, db_session):
        """Test seeding default categories"""
        from app.models.category import Category
        
        # Clear existing
        db_session.query(Category).delete()
        db_session.commit()
        
        # Seed
        SeedData.seed_categories(db_session)
        
        # Verify
        categories = db_session.query(Category).all()
        category_names = [c.name for c in categories]
        
        assert len(categories) >= 9
        assert "groceries" in category_names
        assert "dining" in category_names
        assert "income" in category_names
    
    def test_seed_test_user(self, db_session):
        """Test creating test user"""
        user = SeedData.seed_test_user(db_session)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
    
    def test_seed_test_user_idempotent(self, db_session):
        """Test seeding test user is idempotent"""
        user1 = SeedData.seed_test_user(db_session)
        user2 = SeedData.seed_test_user(db_session)
        
        # Should return same user
        assert user1.id == user2.id
        assert user1.email == user2.email
