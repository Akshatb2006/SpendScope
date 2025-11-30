from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DeduplicationService:
    @staticmethod
    def is_duplicate(db: Session, txn_hash: str) -> bool:
        try:
            return db.query(Transaction).filter(
                Transaction.hash == txn_hash
            ).first() is not None
        except Exception as e:
            logger.error(f"Dedup check error: {e}")
            return False
    
    @staticmethod
    def find_existing_transaction(
        db: Session,
        provider_txn_id: str,
        account_id: int
    ) -> Optional[Transaction]:
        try:
            return db.query(Transaction).filter(
                Transaction.provider_txn_id == provider_txn_id,
                Transaction.account_id == account_id
            ).first()
        except Exception as e:
            logger.error(f"Find transaction error: {e}")
            return None
    
    @staticmethod
    def mark_as_duplicate(db: Session, transaction: Transaction):
        transaction.is_duplicate = True
        db.commit()
