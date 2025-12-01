#!/usr/bin/env python3
"""
Quick script to seed test data for a user
Usage: python seed_user_data.py <user_id>
"""

import sys
# Import database first
from app.database import SessionLocal
# Import ALL models to ensure relationships are registered
from app.models import user, account, transaction, category, budget, audit_log, sync_cursor
# Now import specific classes
from app.models.account import Account, AccountType
from app.models.transaction import Transaction
from app.models.category import Category
from app.generator.transaction_generator import TransactionGenerator
from datetime import datetime, timezone, timedelta
from dateutil import parser as date_parser
import random

def seed_user_accounts(user_id: int):
    """Seed test accounts and transactions for a user"""
    db = SessionLocal()
    
    try:
        print(f"🌱 Seeding data for user ID: {user_id}")
        
        # Create test accounts
        accounts = [
            Account(
                user_id=user_id,
                provider_id="banka",
                provider_account_id="CHECKING_001",
                name="Main Checking",
                account_type=AccountType.CHECKING,
                balance=5000.00,
                currency="USD",
                access_token_encrypted="mock_encrypted_token"
            ),
            Account(
                user_id=user_id,
                provider_id="banka",
                provider_account_id="SAVINGS_001",
                name="Savings",
                account_type=AccountType.SAVINGS,
                balance=15000.00,
                currency="USD",
                access_token_encrypted="mock_encrypted_token"
            ),
            Account(
                user_id=user_id,
                provider_id="bankb",
                provider_account_id="CREDIT_001",
                name="Credit Card",
                account_type=AccountType.CREDIT,
                balance=-1200.00,
                currency="USD",
                access_token_encrypted="mock_encrypted_token"
            )
        ]
        
        for account in accounts:
            db.add(account)
        
        db.commit()
        print(f"✅ Created {len(accounts)} accounts")
        
        # Generate transactions for each account
        total_transactions = 0
        for account in accounts:
            # Generate transactions for the past 30 days
            transactions_data = TransactionGenerator.generate_transactions(
                account_id=account.provider_account_id,
                start_date=datetime.now(timezone.utc) - timedelta(days=30),
                days=30,
                daily_count=3
            )
            
            for txn_data in transactions_data:
                # Parse date string to datetime object if it's a string
                txn_date = txn_data["date"]
                if isinstance(txn_date, str):
                    txn_date = date_parser.isoparse(txn_date)
                
                transaction = Transaction(
                    account_id=account.id,
                    provider_txn_id=txn_data["id"],
                    date=txn_date,
                    amount=txn_data["amount"],
                    description=txn_data["description"],
                    merchant=txn_data.get("merchant", ""),
                    category=txn_data["category"],
                    hash=txn_data.get("hash") or None  
                )
                db.add(transaction)
                total_transactions += 1
        
        db.commit()
        print(f"✅ Created {total_transactions} transactions")
        
        # Ensure categories exist
        existing_categories = db.query(Category).count()
        if existing_categories == 0:
            from app.generator.seed_data import SeedData
            SeedData.seed_categories(db)
            print("✅ Created default categories")
        
        print("\n🎉 Data seeding complete!")
        print(f"\nYou can now:")
        print(f"  • List accounts: curl -H 'Authorization: Bearer $LOCAL_TOKEN' http://localhost:8000/accounts")
        print(f"  • List transactions: curl -H 'Authorization: Bearer $LOCAL_TOKEN' http://localhost:8000/transactions")
        print(f"  • Or visit: http://localhost:8000/docs\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_id = int(sys.argv[1])
    else:
        user_id = 5  # Default to your local test user
    
    seed_user_accounts(user_id)
