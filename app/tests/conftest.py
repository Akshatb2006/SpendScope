import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.account import Account, AccountType
from app.core.security import get_password_hash, create_access_token
from datetime import datetime, timezone

# Use in-memory SQLite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with the database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    """Return authentication headers for the test user."""
    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}

from app.core.security import encrypt_token

@pytest.fixture
def test_account(db_session, test_user):
    """Create a test account for the test user."""
    account = Account(
        user_id=test_user.id,
        provider_id="test_provider",
        provider_account_id="test_account_123",
        account_type=AccountType.CHECKING,
        name="Test Checking Account",
        balance=1000.0,
        currency="USD",
        last_synced=datetime.now(timezone.utc),
        access_token_encrypted=encrypt_token("fake_token")
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account

from app.providers.base_provider import BaseProvider
from app.normalization.base_normalizer import BaseNormalizer
from app.schemas.transaction_schemas import TransactionBase
from app.schemas.account_schemas import AccountCreate
from app.providers.provider_registry import provider_registry
from app.services.sync_service import SyncService
from typing import List, Dict, Any

class MockProvider(BaseProvider):
    def get_provider_id(self) -> str:
        return "test_provider"
    
    def get_provider_name(self) -> str:
        return "Test Provider"
    
    def fetch_accounts(self, token: str) -> List[Dict[str, Any]]:
        return [{"id": "test_account_123", "name": "Test Account", "type": "checking"}]
    
    def fetch_transactions(self, token: str, account_id: str, since_date: datetime = None) -> List[Dict[str, Any]]:
        return [
            {
                "id": "txn_1",
                "date": "2023-01-01T12:00:00",
                "amount": -50.00,
                "description": "Test Transaction",
                "merchant": "Test Merchant"
            }
        ]

class MockNormalizer(BaseNormalizer):
    def normalize_account(self, raw_account: Dict[str, Any]) -> AccountCreate:
        return AccountCreate(
            provider_account_id=raw_account["id"],
            name=raw_account["name"],
            type=raw_account["type"],
            balance=0.0
        )
    
    def normalize_transaction(self, raw_transaction: Dict[str, Any]) -> TransactionBase:
        return TransactionBase(
            provider_txn_id=raw_transaction["id"],
            date=datetime.fromisoformat(raw_transaction["date"]),
            amount=raw_transaction["amount"],
            description=raw_transaction["description"],
            merchant=raw_transaction["merchant"]
        )

from unittest.mock import patch

@pytest.fixture(autouse=True)
def setup_test_provider():
    """Register mock provider and normalizer for tests."""
    print("DEBUG: Setting up test provider")
    mock_provider = MockProvider()
    mock_normalizer = MockNormalizer()
    
    # Use patch.dict to safely patch the dictionary
    with patch.dict(provider_registry._providers, {"test_provider": mock_provider}):
        original_normalizers = SyncService.NORMALIZERS.copy()
        SyncService.NORMALIZERS["test_provider"] = mock_normalizer
        yield
        SyncService.NORMALIZERS = original_normalizers

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with the database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Debug: Print routes
    print("\nDEBUG: Registered Routes:")
    for route in app.routes:
        print(f"  {route.path} [{route.methods}]")
        
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
