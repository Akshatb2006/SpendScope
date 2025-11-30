from sqlalchemy.orm import Session
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.sync_cursor import SyncCursor
from app.providers.provider_registry import provider_registry
from app.normalization.banka_normalizer import BankANormalizer
from app.normalization.bankb_normalizer import BankBNormalizer
from app.normalization.bankc_normalizer import BankCNormalizer
from app.services.dedup_service import DeduplicationService
from app.services.categorization_service import CategorizationService
from app.services.budget_service import BudgetService
from app.services.delta_history_service import DeltaHistoryService
from app.core.security import decrypt_token
from app.core.hashing import generate_transaction_hash
from app.cache import cache
from datetime import datetime, timezone
import time
import logging

logger = logging.getLogger(__name__)

class SyncService:
    NORMALIZERS = {
        "banka": BankANormalizer(),
        "bankb": BankBNormalizer(),
        "bankc": BankCNormalizer()
    }
    
    @staticmethod
    def sync_account(db: Session, account_id: int) -> dict:
        start_time = time.time()
        
        try:
            account = db.query(Account).filter(Account.id == account_id).first()
            if not account:
                return {"error": "Account not found"}
            
            provider = provider_registry.get_provider(account.provider_id)
            normalizer = SyncService.NORMALIZERS.get(account.provider_id)
            
            if not normalizer:
                return {"error": f"Normalizer not found for {account.provider_id}"}
            
            access_token = decrypt_token(account.access_token_encrypted)
            
            raw_transactions = provider.fetch_transactions(
                access_token,
                account.provider_account_id,
                account.last_synced
            )
            
            records_fetched = len(raw_transactions)
            records_inserted = 0
            records_deduplicated = 0
            records_updated = 0
            
            for raw_txn in raw_transactions:
                try:
                    normalized = normalizer.normalize_transaction(raw_txn)
                    
                    txn_hash = generate_transaction_hash(
                        normalized.date,
                        normalized.amount,
                        normalized.description,
                        account.provider_id
                    )
                    
                    if DeduplicationService.is_duplicate(db, txn_hash):
                        records_deduplicated += 1
                        continue
                    
                    provider_txn_id = (raw_txn.get("id") or 
                                      raw_txn.get("txn_id") or 
                                      raw_txn.get("transaction_id"))
                    
                    existing_txn = DeduplicationService.find_existing_transaction(
                        db, provider_txn_id, account_id
                    )
                    
                    if existing_txn:
                        if existing_txn.amount != normalized.amount:
                            DeltaHistoryService.log_change(
                                db, existing_txn.id, "correction", "amount",
                                str(existing_txn.amount), str(normalized.amount),
                                "system", "Provider correction"
                            )
                            existing_txn.amount = normalized.amount
                        
                        records_updated += 1
                        continue
                    
                    category = CategorizationService.categorize(
                        normalized.description,
                        normalized.merchant,
                        normalized.amount
                    )
                    
                    transaction = Transaction(
                        account_id=account_id,
                        provider_txn_id=provider_txn_id,
                        date=normalized.date,
                        amount=normalized.amount,
                        description=normalized.description,
                        merchant=normalized.merchant,
                        category=category,
                        hash=txn_hash
                    )
                    
                    db.add(transaction)
                    records_inserted += 1
                    
                    db.flush() 
                    DeltaHistoryService.log_change(
                        db, transaction.id, "create", None, None, None,
                        "system", "Sync"
                    )
                    
                    if normalized.amount < 0:
                        BudgetService.update_budget_spending(
                            db, account.user_id, category, normalized.amount
                        )
                    
                except Exception as e:
                    logger.error(f"Error processing transaction: {e}")
                    continue
            
            account.last_synced = datetime.now(timezone.utc)
            account.updated_at = datetime.now(timezone.utc)
            db.commit()
            
            cache.invalidate_pattern(f"account:{account_id}:*")
            cache.invalidate_pattern(f"user:{account.user_id}:*")
            
            duration = time.time() - start_time
            sync_cursor = SyncCursor(
                account_id=account_id,
                provider_id=account.provider_id,
                last_sync_date=datetime.now(timezone.utc),
                status="success",
                records_fetched=records_fetched,
                records_inserted=records_inserted,
                records_deduplicated=records_deduplicated,
                duration_seconds=duration
            )
            db.add(sync_cursor)
            db.commit()
            
            return {
                "status": "success",
                "account_id": account_id,
                "records_fetched": records_fetched,
                "records_inserted": records_inserted,
                "records_deduplicated": records_deduplicated,
                "records_updated": records_updated,
                "duration_seconds": round(duration, 3)
            }
            
        except Exception as e:
            logger.error(f"Sync error for account {account_id}: {e}")
            duration = time.time() - start_time
            
            sync_cursor = SyncCursor(
                account_id=account_id,
                provider_id=account.provider_id if account else "unknown",
                status="failed",
                error_message=str(e),
                duration_seconds=duration
            )
            db.add(sync_cursor)
            db.commit()
            
            return {"status": "error", "message": str(e)}
