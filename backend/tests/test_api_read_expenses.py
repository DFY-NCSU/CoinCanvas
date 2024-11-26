import pytest
from fastapi.testclient import TestClient
import logging
from typing import Dict, List

from app.main import app

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class TestReadExpense:
    """Test expense read operations with pagination"""

    @pytest.fixture
    def client(self):
        """Fixture for TestClient"""
        return TestClient(app)

    @pytest.fixture
    def test_user(self) -> Dict:
        """Fixture for test user credentials"""
        return {
            "email": "test_expense_read@example.com",
            "password": "testpassword123",
            "full_name": "Test Expense Read User"
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
    def create_test_expenses(self, client, auth_headers) -> List[Dict]:
        """Fixture to create multiple test expenses"""
        expenses = []
        # Create 15 test expenses
        for i in range(15):
            expense = {
                "category": f"Category {i}",
                "amount": 10.0 + i,
                "payment_method": "Credit Card",
                "description": f"Test expense {i}"
            }
            response = client.post(
                "/expenses/",
                json=expense,
                headers=auth_headers
            )
            if response.status_code == 200:
                expenses.append(response.json())
        return expenses

    def test_read_expenses_default_pagination(self, client, auth_headers, create_test_expenses):
        """Test reading expenses with default pagination (no parameters)"""
        response = client.get("/expenses/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 100  # Default limit

    def test_read_expenses_with_limit(self, client, auth_headers, create_test_expenses):
        """Test reading expenses with specific limit"""
        limit = 5
        response = client.get(f"/expenses/?limit={limit}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= limit

    def test_read_expenses_with_skip(self, client, auth_headers, create_test_expenses):
        """Test reading expenses with skip parameter"""
        # First get all expenses
        all_expenses = client.get("/expenses/", headers=auth_headers).json()

        # Then get expenses with skip
        skip = 5
        response = client.get(f"/expenses/?skip={skip}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        if len(all_expenses) > skip:
            assert data[0]["id"] == all_expenses[skip]["id"]

    def test_read_expenses_with_skip_and_limit(self, client, auth_headers, create_test_expenses):
        """Test reading expenses with both skip and limit"""
        skip = 5
        limit = 3
        response = client.get(f"/expenses/?skip={skip}&limit={limit}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= limit

    def test_read_expenses_zero_limit(self, client, auth_headers):
        """Test reading expenses with limit=0"""
        response = client.get("/expenses/?limit=0", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_read_expenses_negative_limit(self, client, auth_headers):
        """Test reading expenses with negative limit"""
        response = client.get("/expenses/?limit=-1", headers=auth_headers)
        assert response.status_code == 422  # Validation error

    def test_read_expenses_negative_skip(self, client, auth_headers):
        """Test reading expenses with negative skip"""
        response = client.get("/expenses/?skip=-1", headers=auth_headers)
        assert response.status_code == 422  # Validation error

    def test_read_expenses_invalid_limit_type(self, client, auth_headers):
        """Test reading expenses with invalid limit type"""
        response = client.get("/expenses/?limit=abc", headers=auth_headers)
        assert response.status_code == 422  # Validation error

    def test_read_expenses_invalid_skip_type(self, client, auth_headers):
        """Test reading expenses with invalid skip type"""
        response = client.get("/expenses/?skip=abc", headers=auth_headers)
        assert response.status_code == 422  # Validation error

    def test_read_expenses_large_limit(self, client, auth_headers):
        """Test reading expenses with very large limit"""
        response = client.get("/expenses/?limit=1000000", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_read_expenses_large_skip(self, client, auth_headers):
        """Test reading expenses with very large skip"""
        response = client.get("/expenses/?skip=1000000", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0  # Should return empty list if skip is beyond total count

    def test_read_expenses_unauthorized(self, client):
        """Test reading expenses without authorization"""
        response = client.get("/expenses/")
        assert response.status_code == 401

    def test_read_expenses_invalid_token(self, client):
        """Test reading expenses with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/expenses/", headers=headers)
        assert response.status_code == 401

    def test_read_expenses_pagination_consistency(self, client, auth_headers, create_test_expenses):
        """Test consistency of paginated results"""
        # Get first page
        limit = 5
        first_page = client.get(f"/expenses/?limit={limit}", headers=auth_headers).json()

        # Get second page
        second_page = client.get(
            f"/expenses/?skip={limit}&limit={limit}",
            headers=auth_headers
        ).json()

        # Check no overlap
        first_page_ids = {expense["id"] for expense in first_page}
        second_page_ids = {expense["id"] for expense in second_page}
        assert not first_page_ids.intersection(second_page_ids)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--disable-warnings"])
