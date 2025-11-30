from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.services.delta_history_service import DeltaHistoryService
from app.schemas.transaction_schemas import TransactionReconcile
import logging

logger = logging.getLogger(__name__)

class ReconciliationService:
    @staticmethod
    def reconcile_transaction(
        db: Session,
        transaction_id: int,
        reconcile_data: TransactionReconcile,
        user_id: int
    ) -> Transaction:
        try:
            transaction = db.query(Transaction).filter(
                Transaction.id == transaction_id
            ).first()
            
            if not transaction:
                raise ValueError("Transaction not found")
            
            # Track all changes
            if reconcile_data.amount is not None and reconcile_data.amount != transaction.amount:
                DeltaHistoryService.log_change(
                    db, transaction_id, "reconcile", "amount",
                    str(transaction.amount), str(reconcile_data.amount),
                    "user", reconcile_data.reason, user_id=user_id
                )
                transaction.amount = reconcile_data.amount
            
            if reconcile_data.description and reconcile_data.description != transaction.description:
                DeltaHistoryService.log_change(
                    db, transaction_id, "reconcile", "description",
                    transaction.description, reconcile_data.description,
                    "user", reconcile_data.reason, user_id=user_id
                )
                transaction.description = reconcile_data.description
            
            if reconcile_data.category and reconcile_data.category != transaction.category:
                DeltaHistoryService.log_change(
                    db, transaction_id, "reconcile", "category",
                    transaction.category, reconcile_data.category,
                    "user", reconcile_data.reason, user_id=user_id
                )
                transaction.category = reconcile_data.category
            
            if reconcile_data.merchant and reconcile_data.merchant != transaction.merchant:
                DeltaHistoryService.log_change(
                    db, transaction_id, "reconcile", "merchant",
                    transaction.merchant, reconcile_data.merchant,
                    "user", reconcile_data.reason, user_id=user_id
                )
                transaction.merchant = reconcile_data.merchant
            
            transaction.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(transaction)
            
            return transaction
            
        except Exception as e:
            logger.error(f"Reconciliation error: {e}")
            db.rollback()
            raise