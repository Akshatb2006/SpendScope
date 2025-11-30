import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    """Test user registration"""
    response = client.post("/auth/register", json={
        "email": "newuser@test.com",
        "password": "testpass123",
        "full_name": "Test User"
    })
    assert response.status_code in [200, 400]  # 400 if already exists

def test_login():
    """Test user login"""
    # Register first
    client.post("/auth/register", json={
        "email": "testuser@test.com",
        "password": "testpass123"
    })
    
    # Login
    response = client.post("/auth/login", json={
        "email": "testuser@test.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()