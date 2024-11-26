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

    def test_create_expense_with_required_fields_only(self, client, auth_headers):
        """Test expense creation with only required fields and no optional fields"""
        expense = {
            "date": datetime.now(timezone.utc).isoformat(),
            "category": "Utilities",
            "amount": 100.00,
            "payment_method": "Bank Transfer"
        }
        response = client.post("/expenses/", json=expense, headers=auth_headers)
        assert response.status_code == 200

    def test_create_expense_with_lowest_valid_amount(self, client, auth_headers):
        """Test expense creation with the smallest valid positive amount"""
        expense = {
            "date": datetime.now(timezone.utc).isoformat(),
            "category": "Groceries",
            "amount": 0.01,
            "payment_method": "Cash"
        }
        response = client.post("/expenses/", json=expense, headers=auth_headers)
        assert response.status_code == 200

    def test_create_expense_with_max_category_length(self, client, auth_headers):
        """Test expense creation with maximum category name length"""
        expense = {
            "date": datetime.now(timezone.utc).isoformat(),
            "category": "a" * 40,  # Adjusted to match system's length limit
            "amount": 50.00,
            "payment_method": "Credit Card",
            "description": "Utility bills payment"
        }
        response = client.post("/expenses/", json=expense, headers=auth_headers)
        assert response.status_code == 200

    def test_create_expense_with_multilingual_description(self, client, auth_headers):
        """Test expense creation with multilingual text in the description"""
        expense = {
            "date": datetime.now(timezone.utc).isoformat(),
            "category": "Food",
            "amount": 30.00,
            "payment_method": "Debit Card",
            "description": "Cena en restaurante - 晚餐"
        }
        response = client.post("/expenses/", json=expense, headers=auth_headers)
        assert response.status_code == 200

    def test_create_expense_with_extra_fields_ignored(self, client, auth_headers):
        """Test expense creation with extra fields that should be ignored by the API"""
        expense = {
            "date": datetime.now(timezone.utc).isoformat(),
            "category": "Travel",
            "amount": 150.00,
            "payment_method": "PayPal",
            "description": "Flight tickets",
            "extra_field": "This should be ignored"
        }
        response = client.post("/expenses/", json=expense, headers=auth_headers)
        assert response.status_code == 200
        assert "extra_field" not in response.json()

    def test_create_expense_with_symbols_in_category(self, client, auth_headers):
        """Test expense creation with symbols in the category name"""
        expense = {
            "date": datetime.now(timezone.utc).isoformat(),
            "category": "Entertainment & Leisure",
            "amount": 75.00,
            "payment_method": "Credit Card",
            "description": "Concert tickets"
        }
        response = client.post("/expenses/", json=expense, headers=auth_headers)
        assert response.status_code == 200

    def test_create_expense_with_high_precision_amount(self, client, auth_headers):
        """Test expense creation with an amount having high precision"""
        expense = {
            "date": datetime.now(timezone.utc).isoformat(),
            "category": "Investment",
            "amount": 1234.56,
            "payment_method": "Bank Transfer",
            "description": "Stock purchase"
        }
        response = client.post("/expenses/", json=expense, headers=auth_headers)
        assert response.status_code == 200
        assert round(response.json()["amount"], 2) == 1234.56

    def test_create_duplicate_expense(self, client, auth_headers, valid_expense):
        """Test creating duplicate expenses and ensure both are created"""
        response1 = client.post("/expenses/", json=valid_expense, headers=auth_headers)
        response2 = client.post("/expenses/", json=valid_expense, headers=auth_headers)
        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_list_expenses_after_creation(self, client, auth_headers, valid_expense):
        """Test listing all expenses after creating one"""
        client.post("/expenses/", json=valid_expense, headers=auth_headers)
        response = client.get("/expenses/", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) > 0

    def test_create_expense_with_timezone_aware_date(self, client, auth_headers):
        """Test expense creation with a timezone-aware date"""
        tz_aware_date = datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat()
        expense = {
            "date": tz_aware_date,
            "category": "Gifts",
            "amount": 200.00,
            "payment_method": "Credit Card",
            "description": "Birthday gift"
        }
        response = client.post("/expenses/", json=expense, headers=auth_headers)
        assert response.status_code == 200



if __name__ == "__main__":
    pytest.main([__file__, "-v", "--disable-warnings"])
