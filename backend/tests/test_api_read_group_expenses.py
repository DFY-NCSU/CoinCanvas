import pytest
import requests
import logging
from typing import Dict, List
import time
from datetime import datetime, timezone, timedelta

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://127.0.0.1:8000"


class TestGetGroupExpenses:
    """Test getting group expenses endpoints"""

    @pytest.fixture
    def test_users(self) -> List[Dict]:
        """Fixture for multiple test user credentials"""
        return [
            {
                "email": f"test_get_expenses_{i}_{time.time()}@example.com",
                "password": "testpassword123",
                "full_name": f"Test Get Expenses User {i}"
            } for i in range(3)
        ]

    @pytest.fixture
    def auth_tokens(self, test_users) -> List[str]:
        """Fixture to create users and get their auth tokens"""
        tokens = []
        for user in test_users:
            # Create test user
            requests.post(f"{BASE_URL}/users/", json=user)

            # Get token
            response = requests.post(
                f"{BASE_URL}/token",
                data={
                    "username": user["email"],
                    "password": user["password"]
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            assert response.status_code == 200, f"Failed to get auth token for {user['email']}"
            tokens.append(response.json()["access_token"])
        return tokens

    @pytest.fixture
    def auth_headers_list(self, auth_tokens) -> List[Dict]:
        """Fixture for authorization headers for all users"""
        return [
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            } for token in auth_tokens
        ]

    @pytest.fixture
    def test_group(self) -> Dict:
        """Fixture for test group data"""
        return {
            "name": f"Test Get Expenses Group {time.time()}"
        }

    @pytest.fixture
    def created_group(self, auth_headers_list, test_group) -> Dict:
        """Fixture to create a test group and add all users to it"""
        # Create group with first user
        response = requests.post(
            f"{BASE_URL}/groups/",
            json=test_group,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 200
        group_data = response.json()

        # Add other users to the group
        for headers in auth_headers_list[1:]:
            join_response = requests.post(
                f"{BASE_URL}/groups/{group_data['id']}/join",
                headers=headers
            )
            assert join_response.status_code == 200

        return group_data

    @pytest.fixture
    def sample_expenses(self) -> List[Dict]:
        """Fixture for sample expenses with different categories and amounts"""
        base_date = datetime.now(timezone.utc)
        return [
            {
                "date": (base_date - timedelta(days=i)).isoformat(),
                "category": category,
                "amount": amount,
                "description": f"Test expense for {category}",
                "split_type": "equal"
            }
            for i, (category, amount) in enumerate([
                ("Food", 150.00),
                ("Transportation", 50.00),
                ("Utilities", 200.00),
                ("Entertainment", 80.00),
                ("Rent", 1000.00)
            ])
        ]

    @pytest.fixture
    def group_with_expenses(
        self, auth_headers_list, created_group, sample_expenses
    ) -> Dict:
        """Fixture to create a group with multiple expenses"""
        # Create multiple expenses in the group
        for expense in sample_expenses:
            response = requests.post(
                f"{BASE_URL}/groups/{created_group['id']}/expenses",
                json=expense,
                headers=auth_headers_list[0]
            )
            assert response.status_code == 200

        return created_group

    def test_get_expenses_success(self, auth_headers_list, group_with_expenses):
        """Test successful retrieval of group expenses"""
        response = requests.get(
            f"{BASE_URL}/groups/{group_with_expenses['id']}/expenses/",
            headers=auth_headers_list[0]
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Verify expense structure
        for expense in data:
            assert "id" in expense
            assert "date" in expense
            assert "category" in expense
            assert "amount" in expense
            assert "description" in expense
            assert "splits" in expense
            assert "paid_by" in expense
            assert "user_split" in expense
            assert "is_paid_by_user" in expense

    def test_get_expenses_pagination(self, auth_headers_list, group_with_expenses):
        """Test pagination of group expenses"""
        # Test with limit of 2
        response = requests.get(
            f"{BASE_URL}/groups/{group_with_expenses['id']}/expenses/?skip=0&limit=2",
            headers=auth_headers_list[0]
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

        # Test with skip
        response_skip = requests.get(
            f"{BASE_URL}/groups/{group_with_expenses['id']}/expenses/?skip=2&limit=2",
            headers=auth_headers_list[0]
        )
        assert response_skip.status_code == 200
        data_skip = response_skip.json()
        # Verify different expenses are returned
        if len(data) > 0 and len(data_skip) > 0:
            assert data[0]["id"] != data_skip[0]["id"]

    def test_get_expenses_unauthorized(self, group_with_expenses):
        """Test getting expenses without authorization"""
        response = requests.get(
            f"{BASE_URL}/groups/{group_with_expenses['id']}/expenses/"
        )
        assert response.status_code == 401

    def test_get_expenses_invalid_group(self, auth_headers_list):
        """Test getting expenses for non-existent group"""
        response = requests.get(
            f"{BASE_URL}/groups/99999/expenses/",
            headers=auth_headers_list[0]
        )
        assert response.status_code == 404

    def test_get_expenses_non_member(
        self, group_with_expenses, test_users
    ):
        """Test getting expenses as non-group member"""
        # Create a new user who is not a member of the group
        new_user = {
            "email": f"non_member_get_{time.time()}@example.com",
            "password": "testpassword123",
            "full_name": "Non Member Get User"
        }
        requests.post(f"{BASE_URL}/users/", json=new_user)
        token_response = requests.post(
            f"{BASE_URL}/token",
            data={
                "username": new_user["email"],
                "password": new_user["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        non_member_headers = {
            "Authorization": f"Bearer {token_response.json()['access_token']}",
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"{BASE_URL}/groups/{group_with_expenses['id']}/expenses/",
            headers=non_member_headers
        )
        assert response.status_code == 403

    def test_verify_expense_split_info(
        self, auth_headers_list, group_with_expenses
    ):
        """Test that expense split information is correct for different users"""
        response = requests.get(
            f"{BASE_URL}/groups/{group_with_expenses['id']}/expenses/",
            headers=auth_headers_list[0]
        )
        assert response.status_code == 200
        data = response.json()

        # Check first user's view (expense creator)
        for expense in data:
            assert "user_split" in expense
            assert "is_paid_by_user" in expense
            assert isinstance(expense["user_split"], (int, float))
            assert isinstance(expense["is_paid_by_user"], bool)
            assert expense["is_paid_by_user"] is True  # First user created all expenses

        # Check second user's view
        response2 = requests.get(
            f"{BASE_URL}/groups/{group_with_expenses['id']}/expenses/",
            headers=auth_headers_list[1]
        )
        assert response2.status_code == 200
        data2 = response2.json()

        for expense in data2:
            assert "user_split" in expense
            assert "is_paid_by_user" in expense
            assert isinstance(expense["user_split"], (int, float))
            assert isinstance(expense["is_paid_by_user"], bool)
            assert expense["is_paid_by_user"] is False  # Second user didn't create any expenses

    def test_get_expenses_negative_limit(self, auth_headers_list, group_with_expenses):
        """Test reading expenses with negative limit"""
        response = requests.get(
            f"{BASE_URL}/groups/{group_with_expenses['id']}/expenses/?limit=-1",
            headers=auth_headers_list[0]
        )
        assert response.status_code == 422

    def test_get_expenses_negative_skip(self, auth_headers_list, group_with_expenses):
        """Test reading expenses with negative skip"""
        response = requests.get(
            f"{BASE_URL}/groups/{group_with_expenses['id']}/expenses/?skip=-1",
            headers=auth_headers_list[0]
        )
        assert response.status_code == 422  # Validation error

    def test_get_expenses_invalid_limit_type(self, auth_headers_list, group_with_expenses):
        """Test reading expenses with invalid limit type"""
        response = requests.get(
            f"{BASE_URL}/groups/{group_with_expenses['id']}/expenses/?limit=abc",
            headers=auth_headers_list[0]
        )
        assert response.status_code == 422  # Validation error

    def test_get_expenses_invalid_skip_type(self, auth_headers_list, group_with_expenses):
        """Test reading expenses with invalid skip type"""
        response = requests.get(
            f"{BASE_URL}/groups/{group_with_expenses['id']}/expenses/?skip=abc",
            headers=auth_headers_list[0]
        )
        assert response.status_code == 422  # Validation error

    def test_get_expenses_different_users_same_data(
        self, auth_headers_list, group_with_expenses
    ):
        """Test that different users see the same basic expense data"""
        # Get expenses as first user
        response1 = requests.get(
            f"{BASE_URL}/groups/{group_with_expenses['id']}/expenses/",
            headers=auth_headers_list[0]
        )
        data1 = response1.json()

        # Get expenses as second user
        response2 = requests.get(
            f"{BASE_URL}/groups/{group_with_expenses['id']}/expenses/",
            headers=auth_headers_list[1]
        )
        data2 = response2.json()

        # Compare basic expense data (excluding user-specific fields)
        assert len(data1) == len(data2)
        for exp1, exp2 in zip(data1, data2):
            assert exp1["id"] == exp2["id"]
            assert exp1["amount"] == exp2["amount"]
            assert exp1["category"] == exp2["category"]
            assert exp1["description"] == exp2["description"]
            assert exp1["date"] == exp2["date"]

    def test_get_expenses_empty_group(self, auth_headers_list, created_group):
        """Test getting expenses from a group with no expenses"""
        response = requests.get(
            f"{BASE_URL}/groups/{created_group['id']}/expenses/",
            headers=auth_headers_list[0]
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_expenses_expired_token(self, group_with_expenses):
        """Test getting expenses with expired token"""
        headers = {
            "Authorization": "Bearer expired.token.here",
            "Content-Type": "application/json"
        }
        response = requests.get(
            f"{BASE_URL}/groups/{group_with_expenses['id']}/expenses/",
            headers=headers
        )
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--disable-warnings"])
