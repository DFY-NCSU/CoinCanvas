import pytest
import requests
import logging
from typing import Dict, List
import time
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://127.0.0.1:8000"


class TestGroupExpenses:
    """Test group expense-related endpoints"""

    @pytest.fixture
    def test_users(self) -> List[Dict]:
        """Fixture for multiple test user credentials"""
        return [
            {
                "email": f"test_group_expense_{i}_{time.time()}@example.com",
                "password": "testpassword123",
                "full_name": f"Test Group Expense User {i}"
            } for i in range(3)  # Create 3 test users
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
            "name": f"Test Expense Group {time.time()}"
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
    def valid_equal_split_expense(self) -> Dict:
        """Fixture for valid expense with equal split"""
        return {
            "date": datetime.now(timezone.utc).isoformat(),
            "category": "Groceries",
            "amount": 300.00,
            "description": "Weekly groceries",
            "split_type": "equal"
        }

    @pytest.fixture
    def valid_custom_split_expense(self, test_users) -> Dict:
        """Fixture for valid expense with custom split"""
        return {
            "date": datetime.now(timezone.utc).isoformat(),
            "category": "Rent",
            "amount": 1000.00,
            "description": "Monthly rent",
            "split_type": "custom",
            "custom_splits": {
                "1": 50,  # 50%
                "2": 30,  # 30%
                "3": 20   # 20%
            }
        }

    def test_create_equal_split_expense_success(
        self, auth_headers_list, created_group, valid_equal_split_expense
    ):
        """Test successful creation of equally split expense"""
        response = requests.post(
            f"{BASE_URL}/groups/{created_group['id']}/expenses",
            json=valid_equal_split_expense,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == valid_equal_split_expense["category"]
        assert float(data["amount"]) == valid_equal_split_expense["amount"]
        assert len(data["splits"]) == 3  # One split for each user
        # Verify each split is equal
        expected_split_amount = valid_equal_split_expense["amount"] / 3
        for split in data["splits"]:
            assert abs(float(split["amount"]) - expected_split_amount) < 0.01

    def test_create_custom_split_expense_success(
        self, auth_headers_list, created_group, valid_custom_split_expense
    ):
        """Test successful creation of custom split expense"""
        response = requests.post(
            f"{BASE_URL}/groups/{created_group['id']}/expenses",
            json=valid_custom_split_expense,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == valid_custom_split_expense["category"]
        assert float(data["amount"]) == valid_custom_split_expense["amount"]
        assert len(data["splits"]) == 3

        # Verify custom split amounts
        for split in data["splits"]:
            user_percentage = valid_custom_split_expense["custom_splits"][str(split["user_id"])]
            expected_amount = (user_percentage / 100) * valid_custom_split_expense["amount"]
            assert abs(float(split["amount"]) - expected_amount) < 0.01

    def test_create_expense_unauthorized(self, created_group, valid_equal_split_expense):
        """Test expense creation without authorization"""
        response = requests.post(
            f"{BASE_URL}/groups/{created_group['id']}/expenses",
            json=valid_equal_split_expense
        )
        assert response.status_code == 401

    def test_create_expense_invalid_group(
        self, auth_headers_list, valid_equal_split_expense
    ):
        """Test creating expense for non-existent group"""
        response = requests.post(
            f"{BASE_URL}/groups/99999/expenses",
            json=valid_equal_split_expense,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 404

    def test_create_expense_negative_amount(
        self, auth_headers_list, created_group, valid_equal_split_expense
    ):
        """Test expense creation with negative amount"""
        valid_equal_split_expense["amount"] = -100.00
        response = requests.post(
            f"{BASE_URL}/groups/{created_group['id']}/expenses",
            json=valid_equal_split_expense,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 422

    def test_create_custom_split_invalid_percentages(
        self, auth_headers_list, created_group, valid_custom_split_expense
    ):
        """Test custom split with invalid percentage total"""
        valid_custom_split_expense["custom_splits"] = {
            "1": 60,  # Total > 100%
            "2": 30,
            "3": 20
        }
        response = requests.post(
            f"{BASE_URL}/groups/{created_group['id']}/expenses",
            json=valid_custom_split_expense,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 400

    def test_create_custom_split_missing_users(
        self, auth_headers_list, created_group, valid_custom_split_expense
    ):
        """Test custom split with missing users"""
        valid_custom_split_expense["custom_splits"] = {
            "1": 70,  # Missing user 3
            "2": 30
        }
        response = requests.post(
            f"{BASE_URL}/groups/{created_group['id']}/expenses",
            json=valid_custom_split_expense,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 200

    @pytest.mark.parametrize("field", ["date", "category", "amount"])
    def test_create_expense_missing_required_fields(
        self, auth_headers_list, created_group, valid_equal_split_expense, field
    ):
        """Test expense creation with missing required fields"""
        # required_fields = ["date", "category", "amount", "split_type"]
        invalid_expense = valid_equal_split_expense.copy()
        del invalid_expense[field]
        response = requests.post(
            f"{BASE_URL}/groups/{created_group['id']}/expenses",
            json=invalid_expense,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 422

    def test_create_expense_invalid_split_type(
        self, auth_headers_list, created_group, valid_equal_split_expense
    ):
        """Test expense creation with invalid split type"""
        valid_equal_split_expense["split_type"] = "invalid_type"
        response = requests.post(
            f"{BASE_URL}/groups/{created_group['id']}/expenses",
            json=valid_equal_split_expense,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 400

    def test_create_custom_split_zero_percentage(
        self, auth_headers_list, created_group, valid_custom_split_expense
    ):
        """Test custom split with zero percentage"""
        valid_custom_split_expense["custom_splits"] = {
            "1": 0,    # Invalid: zero percentage
            "2": 50,
            "3": 50
        }
        response = requests.post(
            f"{BASE_URL}/groups/{created_group['id']}/expenses",
            json=valid_custom_split_expense,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 200

    def test_create_expense_future_date(
        self, auth_headers_list, created_group, valid_equal_split_expense
    ):
        """Test expense creation with future date"""
        future_date = datetime(2025, 12, 31, 12, 0, tzinfo=timezone.utc).isoformat()
        valid_equal_split_expense["date"] = future_date
        response = requests.post(
            f"{BASE_URL}/groups/{created_group['id']}/expenses",
            json=valid_equal_split_expense,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 200  # Assuming future dates are allowed

    def test_create_expense_non_member(
        self, auth_headers_list, created_group, valid_equal_split_expense, test_users
    ):
        """Test expense creation by non-group member"""
        # Create a new user who is not a member of the group
        new_user = {
            "email": f"non_member_{time.time()}@example.com",
            "password": "testpassword123",
            "full_name": "Non Member User"
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

        response = requests.post(
            f"{BASE_URL}/groups/{created_group['id']}/expenses",
            json=valid_equal_split_expense,
            headers=non_member_headers
        )
        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--disable-warnings"])
