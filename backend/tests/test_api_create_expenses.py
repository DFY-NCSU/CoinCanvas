import pytest
import requests
import logging
from typing import Dict
import time

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://127.0.0.1:8000"


class TestCreateExpense:
    """Test expense-related endpoints"""

    @pytest.fixture
    def test_user(self) -> Dict:
        """Fixture for test user credentials"""
        return {
            "email": f"test_expense_{time.time()}@example.com",
            "password": "testpassword123",
            "full_name": "Test Expense User"
        }

    @pytest.fixture(autouse=True)
    def auth_token(self, test_user) -> str:
        """Fixture to create user and get auth token"""
        # Create test user
        requests.post(f"{BASE_URL}/users/", json=test_user)

        # Get token
        response = requests.post(
            f"{BASE_URL}/token",
            data={
                "username": test_user["email"],
                "password": test_user["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200, "Failed to get auth token"
        return response.json()["access_token"]

    @pytest.fixture
    def auth_headers(self, auth_token) -> Dict:
        """Fixture for authorization headers"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

    @pytest.fixture
    def valid_expense(self) -> Dict:
        """Fixture for valid expense data"""
        return {
            "category": "Food",
            "amount": 25.50,
            "payment_method": "Credit Card",
            "description": "Lunch at restaurant"
        }

    def test_create_expense_success(self, auth_headers, valid_expense):
        """Test successful expense creation"""
        response = requests.post(
            f"{BASE_URL}/expenses/",
            json=valid_expense,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == valid_expense["category"]
        assert float(data["amount"]) == valid_expense["amount"]
        assert data["payment_method"] == valid_expense["payment_method"]
        assert data["description"] == valid_expense["description"]
        assert "id" in data
        assert "date" in data

    def test_create_expense_without_description(self, auth_headers, valid_expense):
        """Test expense creation without optional description"""
        expense_no_desc = valid_expense.copy()
        del expense_no_desc["description"]
        response = requests.post(
            f"{BASE_URL}/expenses/",
            json=expense_no_desc,
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "id" in response.json()

    def test_create_expense_unauthorized(self, valid_expense):
        """Test expense creation without authorization"""
        response = requests.post(
            f"{BASE_URL}/expenses/",
            json=valid_expense
        )
        assert response.status_code == 401

    def test_create_expense_invalid_token(self, valid_expense):
        """Test expense creation with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.post(
            f"{BASE_URL}/expenses/",
            json=valid_expense,
            headers=headers
        )
        assert response.status_code == 401

    @pytest.mark.parametrize("field", ["category", "amount", "payment_method"])
    def test_missing_required_fields(self, auth_headers, valid_expense, field):
        """Test expense creation with missing required fields"""
        invalid_expense = valid_expense.copy()
        del invalid_expense[field]
        response = requests.post(
            f"{BASE_URL}/expenses/",
            json=invalid_expense,
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_invalid_amount_type(self, auth_headers, valid_expense):
        """Test expense creation with invalid amount type"""
        invalid_expense = valid_expense.copy()
        invalid_expense["amount"] = "not a number"
        response = requests.post(
            f"{BASE_URL}/expenses/",
            json=invalid_expense,
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_negative_amount(self, auth_headers, valid_expense):
        """Test expense creation with negative amount"""
        invalid_expense = valid_expense.copy()
        invalid_expense["amount"] = -50.00
        response = requests.post(
            f"{BASE_URL}/expenses/",
            json=invalid_expense,
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_zero_amount(self, auth_headers, valid_expense):
        """Test expense creation with zero amount"""
        valid_expense["amount"] = 0
        response = requests.post(
            f"{BASE_URL}/expenses/",
            json=valid_expense,
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_empty_strings(self, auth_headers, valid_expense):
        """Test expense creation with empty strings"""
        invalid_expense = valid_expense.copy()
        invalid_expense["category"] = ""
        invalid_expense["payment_method"] = ""
        response = requests.post(
            f"{BASE_URL}/expenses/",
            json=invalid_expense,
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_large_amount(self, auth_headers, valid_expense):
        """Test expense creation with large amount"""
        valid_expense["amount"] = 999999.99
        response = requests.post(
            f"{BASE_URL}/expenses/",
            json=valid_expense,
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_long_description(self, auth_headers, valid_expense):
        """Test expense creation with long description"""
        valid_expense["description"] = "a" * 1000
        response = requests.post(
            f"{BASE_URL}/expenses/",
            json=valid_expense,
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_special_characters(self, auth_headers, valid_expense):
        """Test expense creation with special characters"""
        valid_expense["category"] = "Food & Drinks"
        valid_expense["description"] = "Lunch @ Joe's Café"
        valid_expense["payment_method"] = "Friend's Card"
        response = requests.post(
            f"{BASE_URL}/expenses/",
            json=valid_expense,
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_get_expenses(self, auth_headers):
        """Test getting all expenses"""
        response = requests.get(
            f"{BASE_URL}/expenses/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--disable-warnings"])
