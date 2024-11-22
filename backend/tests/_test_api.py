import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..app.database import Base
from ..app.main import app, get_db
import os

# Use a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def user_token(test_db):
    # Create a test user and get token
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    
    # Login and get token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]

def test_create_user(test_db):
    response = client.post(
        "/users/",
        json={
            "email": "user@example.com",
            "password": "password123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data

def test_create_user_duplicate_email(test_db):
    user_data = {
        "email": "duplicate@example.com",
        "password": "password123",
        "full_name": "Test User"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    
    response = client.post("/users/", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login(test_db):
    # Create user first
    user_data = {
        "email": "login@example.com",
        "password": "password123",
        "full_name": "Login Test User"
    }
    client.post("/users/", json=user_data)
    
    # Try logging in
    response = client.post(
        "/token",
        data={
            "username": user_data["email"],
            "password": user_data["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_create_expense(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    expense_data = {
        "category": "Food",
        "amount": 25.50,
        "description": "Lunch",
        "payment_method": "Credit Card"
    }
    response = client.post("/expenses/", json=expense_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == expense_data["category"]
    assert data["amount"] == expense_data["amount"]
    assert "id" in data

def test_get_expenses(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # Create some test expenses
    expense_data = [
        {
            "category": "Food",
            "amount": 25.50,
            "description": "Lunch",
            "payment_method": "Credit Card"
        },
        {
            "category": "Transportation",
            "amount": 30.00,
            "description": "Taxi",
            "payment_method": "Cash"
        }
    ]
    
    for expense in expense_data:
        client.post("/expenses/", json=expense, headers=headers)
    
    response = client.get("/expenses/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert isinstance(data, list)

def test_delete_expense(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # Create an expense first
    expense_data = {
        "category": "Food",
        "amount": 25.50,
        "description": "Lunch",
        "payment_method": "Credit Card"
    }
    response = client.post("/expenses/", json=expense_data, headers=headers)
    expense_id = response.json()["id"]
    
    # Delete the expense
    response = client.delete(f"/expenses/{expense_id}", headers=headers)
    assert response.status_code == 200
    
    # Verify it's deleted
    response = client.get("/expenses/", headers=headers)
    expenses = response.json()
    assert not any(expense["id"] == expense_id for expense in expenses)

def test_unauthorized_access():
    # Try accessing expenses without token
    response = client.get("/expenses/")
    assert response.status_code == 401
    
    # Try with invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/expenses/", headers=headers)
    assert response.status_code == 401

def test_invalid_expense_data(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # Test invalid amount
    invalid_expense = {
        "category": "Food",
        "amount": "invalid",
        "description": "Lunch",
        "payment_method": "Credit Card"
    }
    response = client.post("/expenses/", json=invalid_expense, headers=headers)
    assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__])