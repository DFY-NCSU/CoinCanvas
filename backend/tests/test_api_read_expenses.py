import pytest
import requests
import logging
import time
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://127.0.0.1:8000"

class TestReadExpense:
    """Test expense read operations with pagination"""
    
    @pytest.fixture
    def test_user(self) -> Dict:
        """Fixture for test user credentials"""
        return {
            "email": f"test_expense_read_{time.time()}@example.com",
            "password": "testpassword123",
            "full_name": "Test Expense Read User"
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
    def create_test_expenses(self, auth_headers) -> List[Dict]:
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
            response = requests.post(
                f"{BASE_URL}/expenses/",
                json=expense,
                headers=auth_headers
            )
            if response.status_code == 200:
                expenses.append(response.json())
        return expenses

    def test_read_expenses_default_pagination(self, auth_headers, create_test_expenses):
        """Test reading expenses with default pagination (no parameters)"""
        response = requests.get(
            f"{BASE_URL}/expenses/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 100  # Default limit

    def test_read_expenses_with_limit(self, auth_headers, create_test_expenses):
        """Test reading expenses with specific limit"""
        limit = 5
        response = requests.get(
            f"{BASE_URL}/expenses/?limit={limit}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= limit

    def test_read_expenses_with_skip(self, auth_headers, create_test_expenses):
        """Test reading expenses with skip parameter"""
        # First get all expenses
        all_expenses = requests.get(
            f"{BASE_URL}/expenses/",
            headers=auth_headers
        ).json()
        
        # Then get expenses with skip
        skip = 5
        response = requests.get(
            f"{BASE_URL}/expenses/?skip={skip}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        if len(all_expenses) > skip:
            assert data[0]["id"] == all_expenses[skip]["id"]

    def test_read_expenses_with_skip_and_limit(self, auth_headers, create_test_expenses):
        """Test reading expenses with both skip and limit"""
        skip = 5
        limit = 3
        response = requests.get(
            f"{BASE_URL}/expenses/?skip={skip}&limit={limit}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= limit

    def test_read_expenses_zero_limit(self, auth_headers):
        """Test reading expenses with limit=0"""
        response = requests.get(
            f"{BASE_URL}/expenses/?limit=0",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_read_expenses_negative_limit(self, auth_headers):
        """Test reading expenses with negative limit"""
        response = requests.get(
            f"{BASE_URL}/expenses/?limit=-1",
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    def test_read_expenses_negative_skip(self, auth_headers):
        """Test reading expenses with negative skip"""
        response = requests.get(
            f"{BASE_URL}/expenses/?skip=-1",
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    def test_read_expenses_invalid_limit_type(self, auth_headers):
        """Test reading expenses with invalid limit type"""
        response = requests.get(
            f"{BASE_URL}/expenses/?limit=abc",
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    def test_read_expenses_invalid_skip_type(self, auth_headers):
        """Test reading expenses with invalid skip type"""
        response = requests.get(
            f"{BASE_URL}/expenses/?skip=abc",
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    def test_read_expenses_large_limit(self, auth_headers):
        """Test reading expenses with very large limit"""
        response = requests.get(
            f"{BASE_URL}/expenses/?limit=1000000",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_read_expenses_large_skip(self, auth_headers):
        """Test reading expenses with very large skip"""
        response = requests.get(
            f"{BASE_URL}/expenses/?skip=1000000",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0  # Should return empty list if skip is beyond total count

    def test_read_expenses_unauthorized(self):
        """Test reading expenses without authorization"""
        response = requests.get(f"{BASE_URL}/expenses/")
        assert response.status_code == 401

    def test_read_expenses_invalid_token(self):
        """Test reading expenses with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(
            f"{BASE_URL}/expenses/",
            headers=headers
        )
        assert response.status_code == 401

    def test_read_expenses_pagination_consistency(self, auth_headers, create_test_expenses):
        """Test consistency of paginated results"""
        # Get first page
        limit = 5
        first_page = requests.get(
            f"{BASE_URL}/expenses/?limit={limit}",
            headers=auth_headers
        ).json()
        
        # Get second page
        second_page = requests.get(
            f"{BASE_URL}/expenses/?skip={limit}&limit={limit}",
            headers=auth_headers
        ).json()
        
        # Check no overlap
        first_page_ids = {expense["id"] for expense in first_page}
        second_page_ids = {expense["id"] for expense in second_page}
        assert not first_page_ids.intersection(second_page_ids)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--disable-warnings"])