import pytest
from datetime import datetime, timedelta, timezone
from fastapi import status
from app.services.anomaly_service import AnomalyService
from app.models.transaction import Transaction
import statistics

class TestAnomalyDetection:
    
    def create_baseline_transactions(self, db_session, account_id, category, count=30):
        transactions = []
        for i in range(count):
            variance = (i % 5) - 2  # -2, -1, 0, 1, 2
            amount = -50.00 + variance
            
            txn = Transaction(
                account_id=account_id,
                provider_txn_id=f"BASE_{i}",
                date=datetime.now(timezone.utc) - timedelta(days=count-i),
                amount=amount,  
                description=f"Normal {category} transaction",
                merchant="Regular Store",
                category=category,
                hash=f"hash_{i}"
            )
            db_session.add(txn)
            transactions.append(txn)
        db_session.commit()
        return transactions
    
    def test_detect_unusual_amount_anomaly(self, db_session, test_account):
        self.create_baseline_transactions(db_session, test_account.id, "groceries", 30)
        
        anomaly_txn = Transaction(
            account_id=test_account.id,
            provider_txn_id="ANOMALY_001",
            date=datetime.now(timezone.utc),
            amount=-500.00,  
            description="Unusual large purchase",
            merchant="Unknown Store",
            category="groceries",
            hash="anomaly_hash_1"
        )
        db_session.add(anomaly_txn)
        db_session.commit()
        
        anomalies = AnomalyService.detect_anomalies(db_session, test_account.id)
        
        assert len(anomalies) > 0
        assert any(a["transaction_id"] == anomaly_txn.id for a in anomalies)
        assert any(a["type"] == "unusual_amount" for a in anomalies)
    
    def test_detect_new_merchant_anomaly(self, db_session, test_account):
        for i in range(10):
            txn = Transaction(
                account_id=test_account.id,
                provider_txn_id=f"OLD_{i}",
                date=datetime.now(timezone.utc) - timedelta(days=20-i),
                amount=-50.00,
                description="Purchase",
                merchant="Regular Store",
                category="groceries",
                hash=f"old_hash_{i}"
            )
            db_session.add(txn)
        db_session.commit()
        
        new_merchant_txn = Transaction(
            account_id=test_account.id,
            provider_txn_id="NEW_MERCHANT",
            date=datetime.now(timezone.utc),
            amount=-50.00,
            description="Purchase",
            merchant="Brand New Store",
            category="groceries",
            hash="new_merchant_hash"
        )
        db_session.add(new_merchant_txn)
        db_session.commit()
        
        anomalies = AnomalyService.detect_anomalies(db_session, test_account.id)
        
        new_merchant_anomalies = [a for a in anomalies if a["type"] == "new_merchant"]
        assert len(new_merchant_anomalies) > 0
    
    def test_no_anomalies_with_consistent_pattern(self, db_session, test_account):
        self.create_baseline_transactions(db_session, test_account.id, "groceries", 30)
        
        normal_txn = Transaction(
            account_id=test_account.id,
            provider_txn_id="NORMAL",
            date=datetime.now(timezone.utc),
            amount=-50.00,  
            description="Normal purchase",
            merchant="Regular Store",
            category="groceries",
            hash="normal_hash"
        )
        db_session.add(normal_txn)
        db_session.commit()
        
        anomalies = AnomalyService.detect_anomalies(db_session, test_account.id)
        
        unusual_amount_anomalies = [a for a in anomalies if a["type"] == "unusual_amount"]
        normal_flagged = any(a["transaction_id"] == normal_txn.id for a in unusual_amount_anomalies)
        assert not normal_flagged
    
    def test_anomaly_severity_levels(self, db_session, test_account):
        self.create_baseline_transactions(db_session, test_account.id, "dining", 30)
        
        high_severity = Transaction(
            account_id=test_account.id,
            provider_txn_id="HIGH_SEV",
            date=datetime.now(timezone.utc),
            amount=-400.00,  
            description="Extreme purchase",
            merchant="Store",
            category="dining",
            hash="high_sev_hash"
        )
        db_session.add(high_severity)
        db_session.commit()
        
        anomalies = AnomalyService.detect_anomalies(db_session, test_account.id)
        
        high_sev_anomalies = [a for a in anomalies if a.get("severity") == "high"]
        assert len(high_sev_anomalies) > 0
    
    def test_insufficient_data_no_detection(self, db_session, test_account):
        for i in range(3):
            txn = Transaction(
                account_id=test_account.id,
                provider_txn_id=f"MIN_{i}",
                date=datetime.now(timezone.utc) - timedelta(days=i),
                amount=-50.00,
                description="Transaction",
                merchant="Store",
                category="groceries",
                hash=f"min_hash_{i}"
            )
            db_session.add(txn)
        db_session.commit()
        
        anomalies = AnomalyService.detect_anomalies(db_session, test_account.id)
        assert len(anomalies) == 0  

class TestAnomalyEndpoints:
    
    def test_detect_account_anomalies_endpoint(self, client, auth_headers, test_account, db_session):
        for i in range(15):
            txn = Transaction(
                account_id=test_account.id,
                provider_txn_id=f"TXN_{i}",
                date=datetime.now(timezone.utc) - timedelta(days=i),
                amount=-50.00 if i < 14 else -500.00,  
                description="Transaction",
                merchant="Store",
                category="groceries",
                hash=f"hash_{i}"
            )
            db_session.add(txn)
        db_session.commit()
        
        response = client.get(
            f"/anomalies/account/{test_account.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "anomalies" in data
        assert data["account_id"] == test_account.id
    
    def test_anomaly_detection_unauthorized(self, client, auth_headers):
        response = client.get(
            "/anomalies/account/99999",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
