import pytest
from fastapi.testclient import TestClient
from typing import Dict
import logging
from datetime import datetime, timezone, timedelta

from app.main import app

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class TestCreateExpense:
    """Test expense-related endpoints"""

    @pytest.fixture
    def client(self):
        """Fixture for TestClient"""
        return TestClient(app)

    @pytest.fixture
    def test_user(self) -> Dict:
        """Fixture for test user credentials"""
        return {
            "email": "test_expense@example.com",
            "password": "testpassword123",
            "full_name": "Test Expense User"
        }

    @pytest.fixture(autouse=True)
    def setup_test_user(self, client, test_user):
        """Create test user if doesn't exist"""
        response = client.post("/users/", json=test_user)
        if response.status_code not in (200, 400):  # 400 means user exists
            pytest.fail(f"Failed to setup test user: {response.text}")

    @pytest.fixture
    def auth_headers(self, client, test_user) -> Dict:
        """Fixture for authorization headers"""
        response = client.post(
            "/token",
            data={
                "username": test_user["email"],
                "password": test_user["password"],
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200, "Failed to get auth token"
        token = response.json()["access_token"]
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    @pytest.fixture
    def valid_expense(self) -> Dict:
        """Fixture for valid expense data"""
        current_time = datetime.now(timezone.utc).isoformat()
        return {
            "date": current_time,
            "category": "Food",
            "amount": 25.50,
            "payment_method": "Credit Card",
            "description": "Lunch at restaurant"
        }

    def test_create_expense_success(self, client, auth_headers, valid_expense):
        """Test successful expense creation"""
        response = client.post("/expenses/", json=valid_expense, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == valid_expense["category"]
        assert float(data["amount"]) == valid_expense["amount"]
        assert data["payment_method"] == valid_expense["payment_method"]
        assert data["description"] == valid_expense["description"]
        assert "date" in data
        assert "id" in data

    def test_create_expense_without_description(self, client, auth_headers, valid_expense):
        """Test expense creation without optional description"""
        expense_no_desc = valid_expense.copy()
        del expense_no_desc["description"]
        response = client.post("/expenses/", json=expense_no_desc, headers=auth_headers)
        assert response.status_code == 200
        assert "id" in response.json()

    def test_create_expense_unauthorized(self, client, valid_expense):
        """Test expense creation without authorization"""
        response = client.post("/expenses/", json=valid_expense)
        assert response.status_code == 401

    def test_create_expense_invalid_token(self, client, valid_expense):
        """Test expense creation with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/expenses/", json=valid_expense, headers=headers)
        assert response.status_code == 401

    @pytest.mark.parametrize("field", ["date", "category", "amount", "payment_method"])
    def test_missing_required_fields(self, client, auth_headers, valid_expense, field):
        """Test expense creation with missing required fields"""
        invalid_expense = valid_expense.copy()
        del invalid_expense[field]
        response = client.post("/expenses/", json=invalid_expense, headers=auth_headers)
        assert response.status_code == 422

    def test_invalid_amount_type(self, client, auth_headers, valid_expense):
        """Test expense creation with invalid amount type"""
        invalid_expense = valid_expense.copy()
        invalid_expense["amount"] = "not a number"
        response = client.post("/expenses/", json=invalid_expense, headers=auth_headers)
        assert response.status_code == 422

    def test_invalid_date_format(self, client, auth_headers, valid_expense):
        """Test expense creation with invalid date format"""
        invalid_expense = valid_expense.copy()
        invalid_expense["date"] = "not-a-date"
        response = client.post("/expenses/", json=invalid_expense, headers=auth_headers)
        assert response.status_code == 422

    def test_future_date(self, client, auth_headers, valid_expense):
        """Test expense creation with future date"""
        future_date = datetime(2025, 12, 31, 12, 0, tzinfo=timezone.utc).isoformat()
        valid_expense["date"] = future_date
        response = client.post("/expenses/", json=valid_expense, headers=auth_headers)
        assert response.status_code == 200  # Assuming future dates are allowed

    def test_negative_amount(self, client, auth_headers, valid_expense):
        """Test expense creation with negative amount"""
        invalid_expense = valid_expense.copy()
        invalid_expense["amount"] = -50.00
        response = client.post("/expenses/", json=invalid_expense, headers=auth_headers)
        assert response.status_code == 422

    def test_zero_amount(self, client, auth_headers, valid_expense):
        """Test expense creation with zero amount"""
        valid_expense["amount"] = 0
        response = client.post("/expenses/", json=valid_expense, headers=auth_headers)
        assert response.status_code == 200

    def test_empty_strings(self, client, auth_headers, valid_expense):
        """Test expense creation with empty strings"""
        invalid_expense = valid_expense.copy()
        invalid_expense["category"] = ""
        invalid_expense["payment_method"] = ""
        response = client.post("/expenses/", json=invalid_expense, headers=auth_headers)
        assert response.status_code == 422

    def test_large_amount(self, client, auth_headers, valid_expense):
        """Test expense creation with large amount"""
        valid_expense["amount"] = 999999.99
        response = client.post("/expenses/", json=valid_expense, headers=auth_headers)
        assert response.status_code == 200

    def test_long_description(self, client, auth_headers, valid_expense):
        """Test expense creation with long description"""
        valid_expense["description"] = "a" * 1000
        response = client.post("/expenses/", json=valid_expense, headers=auth_headers)
        assert response.status_code == 200

    def test_special_characters(self, client, auth_headers, valid_expense):
        """Test expense creation with special characters"""
        valid_expense["category"] = "Food & Drinks"
        valid_expense["description"] = "Lunch @ Joe's Café"
        valid_expense["payment_method"] = "Friend's Card"
        response = client.post("/expenses/", json=valid_expense, headers=auth_headers)
        assert response.status_code == 200

    def test_get_expenses(self, client, auth_headers):
        """Test getting all expenses"""
        response = client.get("/expenses/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)



if __name__ == "__main__":
    pytest.main([__file__, "-v", "--disable-warnings"])
