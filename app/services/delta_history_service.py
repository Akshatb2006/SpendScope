from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DeltaHistoryService:
    @staticmethod
    def log_change(
        db: Session,
        transaction_id: int,
        action: str,
        field_changed: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        changed_by: str = "system",
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ):
        
        try:
            audit_log = AuditLog(
                transaction_id=transaction_id,
                user_id=user_id,
                action=action,
                field_changed=field_changed,
                old_value=old_value,
                new_value=new_value,
                changed_by=changed_by,
                reason=reason,
                metadata=metadata
            )
            db.add(audit_log)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to log change: {e}")
            db.rollback()
    
    @staticmethod
    def get_transaction_history(db: Session, transaction_id: int):
        return db.query(AuditLog).filter(
            AuditLog.transaction_id == transaction_id
        ).order_by(AuditLog.created_at.desc()).all()