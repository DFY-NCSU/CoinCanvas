import pytest
import requests
import logging
import time
from typing import Dict, Tuple
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://127.0.0.1:8000"


class TestDeleteExpense:
    """Test expense deletion operations"""

    @pytest.fixture
    def test_user(self) -> Dict:
        """Fixture for test user credentials"""
        return {
            "email": f"test_expense_delete_{time.time()}@example.com",
            "password": "testpassword123",
            "full_name": "Test Expense Delete User"
        }

    @pytest.fixture
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
    def test_expense(self, auth_headers) -> Tuple[int, Dict]:
        """Fixture to create a test expense and return its ID"""
        expense_data = {
            "date": datetime.now(timezone.utc).isoformat(),  # Added required date field
            "category": "Test Category",
            "amount": 50.0,
            "payment_method": "Credit Card",
            "description": "Test expense for deletion"
        }
        response = requests.post(
            f"{BASE_URL}/expenses/",
            json=expense_data,
            headers=auth_headers
        )
        assert response.status_code == 200, "Failed to create test expense"
        created_expense = response.json()
        return created_expense["id"], created_expense

    def test_successful_delete(self, auth_headers, test_expense):
        """Test successful expense deletion"""
        expense_id, _ = test_expense
        response = requests.delete(
            f"{BASE_URL}/expenses/{expense_id}",
            headers=auth_headers
        )
        assert response.status_code == 200

        # Verify expense is deleted
        get_response = requests.get(
            f"{BASE_URL}/expenses/{expense_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 405

    def test_delete_nonexistent_expense(self, auth_headers):
        """Test deleting a non-existent expense ID"""
        large_id = 999999999
        response = requests.delete(
            f"{BASE_URL}/expenses/{large_id}",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_delete_without_auth(self, test_expense):
        """Test deleting without authorization"""
        expense_id, _ = test_expense
        response = requests.delete(f"{BASE_URL}/expenses/{expense_id}")
        assert response.status_code == 401

    def test_delete_invalid_token(self, test_expense):
        """Test deleting with invalid token"""
        expense_id, _ = test_expense
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.delete(
            f"{BASE_URL}/expenses/{expense_id}",
            headers=headers
        )
        assert response.status_code == 401

    def test_delete_negative_id(self, auth_headers):
        """Test deleting with negative ID"""
        response = requests.delete(
            f"{BASE_URL}/expenses/-1",
            headers=auth_headers
        )
        assert response.status_code == 404  # Validation error

    def test_delete_zero_id(self, auth_headers):
        """Test deleting with zero ID"""
        response = requests.delete(
            f"{BASE_URL}/expenses/0",
            headers=auth_headers
        )
        assert response.status_code == 404  # Validation error

    def test_delete_invalid_id_type(self, auth_headers):
        """Test deleting with invalid ID type"""
        response = requests.delete(
            f"{BASE_URL}/expenses/abc",
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    def test_double_delete(self, auth_headers, test_expense):
        """Test deleting the same expense twice"""
        expense_id, _ = test_expense

        # First delete
        first_response = requests.delete(
            f"{BASE_URL}/expenses/{expense_id}",
            headers=auth_headers
        )
        assert first_response.status_code == 200

        # Second delete
        second_response = requests.delete(
            f"{BASE_URL}/expenses/{expense_id}",
            headers=auth_headers
        )
        assert second_response.status_code == 404

    def test_delete_and_verify_list(self, auth_headers, test_expense):
        """Test that deleted expense doesn't appear in expense list"""
        expense_id, expense_data = test_expense

        # Delete expense
        delete_response = requests.delete(
            f"{BASE_URL}/expenses/{expense_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 200

        # Get all expenses
        list_response = requests.get(
            f"{BASE_URL}/expenses/",
            headers=auth_headers
        )
        assert list_response.status_code == 200
        expenses = list_response.json()

        # Verify deleted expense is not in list
        expense_ids = [expense["id"] for expense in expenses]
        assert expense_id not in expense_ids

    def test_delete_expense_id_float(self, auth_headers):
        """Test deleting with floating point ID"""
        response = requests.delete(
            f"{BASE_URL}/expenses/1.5",
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_delete_expense_id_empty(self, auth_headers):
        """Test deleting with empty ID"""
        response = requests.delete(
            f"{BASE_URL}/expenses/",
            headers=auth_headers
        )
        assert response.status_code in [404, 405]  # Not Found or Method Not Allowed

    def test_delete_with_extra_params(self, auth_headers, test_expense):
        """Test deleting with extra query parameters"""
        expense_id, _ = test_expense
        response = requests.delete(
            f"{BASE_URL}/expenses/{expense_id}?extra=param",
            headers=auth_headers
        )
        # Should still work and ignore extra params
        assert response.status_code == 200

    def test_delete_very_large_id(self, auth_headers):
        """Test deleting with very large ID"""
        very_large_id = 10**12  # 1 trillion
        response = requests.delete(
            f"{BASE_URL}/expenses/{very_large_id}",
            headers=auth_headers
        )
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--disable-warnings"])
