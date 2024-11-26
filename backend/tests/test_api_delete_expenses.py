import pytest
from fastapi.testclient import TestClient
import logging
from typing import Dict, Tuple
from datetime import datetime, timezone

from app.main import app

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class TestDeleteExpense:
    """Test expense deletion operations"""

    @pytest.fixture
    def client(self):
        """Fixture for TestClient"""
        return TestClient(app)

    @pytest.fixture
    def test_user(self) -> Dict:
        """Fixture for test user credentials"""
        return {
            "email": "test_expense_delete@example.com",
            "password": "testpassword123",
            "full_name": "Test Expense Delete User"
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
    def test_expense(self, client, auth_headers) -> Tuple[int, Dict]:
        """Fixture to create a test expense and return its ID"""
        expense_data = {
            "date": datetime.now(timezone.utc).isoformat(),
            "category": "Test Category",
            "amount": 50.0,
            "payment_method": "Credit Card",
            "description": "Test expense for deletion"
        }
        response = client.post(
            "/expenses/",
            json=expense_data,
            headers=auth_headers
        )
        assert response.status_code == 200, "Failed to create test expense"
        created_expense = response.json()
        return created_expense["id"], created_expense

    def test_successful_delete(self, client, auth_headers, test_expense):
        """Test successful expense deletion"""
        expense_id, _ = test_expense
        response = client.delete(
            f"/expenses/{expense_id}",
            headers=auth_headers
        )
        assert response.status_code == 200

        # Verify expense is deleted
        get_response = client.get(
            f"/expenses/{expense_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 405

    def test_delete_nonexistent_expense(self, client, auth_headers):
        """Test deleting a non-existent expense ID"""
        response = client.delete(
            "/expenses/999999999",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_delete_without_auth(self, client, test_expense):
        """Test deleting without authorization"""
        expense_id, _ = test_expense
        response = client.delete(f"/expenses/{expense_id}")
        assert response.status_code == 401

    def test_delete_invalid_token(self, client, test_expense):
        """Test deleting with invalid token"""
        expense_id, _ = test_expense
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.delete(
            f"/expenses/{expense_id}",
            headers=headers
        )
        assert response.status_code == 401

    def test_delete_negative_id(self, client, auth_headers):
        """Test deleting with negative ID"""
        response = client.delete(
            "/expenses/-1",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_delete_zero_id(self, client, auth_headers):
        """Test deleting with zero ID"""
        response = client.delete(
            "/expenses/0",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_delete_invalid_id_type(self, client, auth_headers):
        """Test deleting with invalid ID type"""
        response = client.delete(
            "/expenses/abc",
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_double_delete(self, client, auth_headers, test_expense):
        """Test deleting the same expense twice"""
        expense_id, _ = test_expense

        # First delete
        first_response = client.delete(
            f"/expenses/{expense_id}",
            headers=auth_headers
        )
        assert first_response.status_code == 200

        # Second delete
        second_response = client.delete(
            f"/expenses/{expense_id}",
            headers=auth_headers
        )
        assert second_response.status_code == 404

    def test_delete_and_verify_list(self, client, auth_headers, test_expense):
        """Test that deleted expense doesn't appear in expense list"""
        expense_id, _ = test_expense

        # Delete expense
        delete_response = client.delete(
            f"/expenses/{expense_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 200

        # Get all expenses
        list_response = client.get(
            "/expenses/",
            headers=auth_headers
        )
        assert list_response.status_code == 200
        expenses = list_response.json()

        # Verify deleted expense is not in list
        expense_ids = [expense["id"] for expense in expenses]
        assert expense_id not in expense_ids

    def test_delete_expense_id_float(self, client, auth_headers):
        """Test deleting with floating point ID"""
        response = client.delete(
            "/expenses/1.5",
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_delete_expense_id_empty(self, client, auth_headers):
        """Test deleting with empty ID"""
        response = client.delete(
            "/expenses/",
            headers=auth_headers
        )
        assert response.status_code in [404, 405]

    def test_delete_with_extra_params(self, client, auth_headers, test_expense):
        """Test deleting with extra query parameters"""
        expense_id, _ = test_expense
        response = client.delete(
            f"/expenses/{expense_id}?extra=param",
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_delete_very_large_id(self, client, auth_headers):
        """Test deleting with very large ID"""
        very_large_id = 10**12  # 1 trillion
        response = client.delete(
            f"/expenses/{very_large_id}",
            headers=auth_headers
        )
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--disable-warnings"])
