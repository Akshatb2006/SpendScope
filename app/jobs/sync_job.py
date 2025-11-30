from app.database import SessionLocal
from app.models.account import Account
from app.services.sync_service import SyncService
from app.cache import cache
import logging

logger = logging.getLogger(__name__)

def run_sync_jobs():
    if not cache.acquire_lock("sync_job", timeout=300):
        logger.info("Sync job already running, skipping")
        return
    
    try:
        db = SessionLocal()
        accounts = db.query(Account).filter(Account.is_active == True).all()
        
        logger.info(f"Starting sync for {len(accounts)} accounts")
        
        for account in accounts:
            try:
                result = SyncService.sync_account(db, account.id)
                logger.info(f"Account {account.id} sync result: {result}")
            except Exception as e:
                logger.error(f"Failed to sync account {account.id}: {e}")
        
        db.close()
        logger.info("Sync job completed")
        
    except Exception as e:
        logger.error(f"Sync job error: {e}")
    finally:
        cache.release_lock("sync_job")