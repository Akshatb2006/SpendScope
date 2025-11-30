import pytest
from datetime import datetime, timedelta
from fastapi import status
from app.services.sync_service import SyncService
from app.models.transaction import Transaction
from app.models.sync_cursor import SyncCursor

class TestSyncService:
    """Test sync service functionality"""
    
    def test_sync_account_success(self, db_session, test_account):
        """Test successful account sync"""
        result = SyncService.sync_account(db_session, test_account.id)
        if result.get("status") != "success":
            print(f"Sync failed with result: {result}")
        
        assert result["status"] == "success"
        assert result["account_id"] == test_account.id
        assert result["records_fetched"] >= 0
        assert result["duration_seconds"] > 0
    
    def test_sync_nonexistent_account(self, db_session):
        """Test syncing non-existent account"""
        result = SyncService.sync_account(db_session, 99999)
        assert "error" in result
    
    def test_sync_creates_transactions(self, db_session, test_account):
        """Test that sync creates transactions"""
        initial_count = db_session.query(Transaction).filter(
            Transaction.account_id == test_account.id
        ).count()
        
        SyncService.sync_account(db_session, test_account.id)
        
        final_count = db_session.query(Transaction).filter(
            Transaction.account_id == test_account.id
        ).count()
        
        assert final_count > initial_count
    
    def test_sync_updates_last_synced(self, db_session, test_account):
        """Test that sync updates last_synced timestamp"""
        original_last_synced = test_account.last_synced
        
        SyncService.sync_account(db_session, test_account.id)
        db_session.refresh(test_account)
        
        assert test_account.last_synced is not None
        if original_last_synced:
            assert test_account.last_synced > original_last_synced
    
    def test_sync_creates_cursor_log(self, db_session, test_account):
        """Test that sync creates cursor log"""
        SyncService.sync_account(db_session, test_account.id)
        
        cursor = db_session.query(SyncCursor).filter(
            SyncCursor.account_id == test_account.id
        ).first()
        
        assert cursor is not None
        assert cursor.status == "success"
        assert cursor.duration_seconds > 0
    
    def test_sync_deduplicates_transactions(self, db_session, test_account):
        """Test that sync deduplicates repeated transactions"""
        # First sync
        result1 = SyncService.sync_account(db_session, test_account.id)
        records_first = result1["records_inserted"]
        
        # Second sync (should deduplicate)
        result2 = SyncService.sync_account(db_session, test_account.id)
        
        assert result2["records_deduplicated"] > 0
        assert result2["records_inserted"] < records_first
    
    def test_sync_categorizes_transactions(self, db_session, test_account):
        """Test that sync categorizes transactions"""
        SyncService.sync_account(db_session, test_account.id)
        
        transactions = db_session.query(Transaction).filter(
            Transaction.account_id == test_account.id
        ).all()
        
        categorized = [t for t in transactions if t.category is not None]
        assert len(categorized) > 0

class TestSyncEndpoints:
    """Test sync API endpoints"""
    
    def test_manual_sync_trigger(self, client, auth_headers, test_account):
        """Test manual sync trigger"""
        response = client.post(
            f"/sync/account/{test_account.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "sync_initiated"
        assert data["account_id"] == test_account.id
    
    def test_sync_logs_retrieval(self, client, auth_headers, test_account, db_session):
        """Test retrieving sync logs"""
        # Create a sync log first
        SyncService.sync_account(db_session, test_account.id)
        
        response = client.get(
            f"/sync/logs/account/{test_account.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "logs" in data
        assert len(data["logs"]) > 0
    
    def test_sync_unauthorized_account(self, client, auth_headers):
        """Test syncing account user doesn't own"""
        response = client.post(
            "/sync/account/99999",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
