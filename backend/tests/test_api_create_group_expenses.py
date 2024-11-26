import pytest
from fastapi.testclient import TestClient
from typing import Dict, List
import logging
from datetime import datetime, timezone

from app.main import app

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class TestGroupExpenses:
    """Test group expense-related endpoints"""

    @pytest.fixture
    def client(self):
        """Fixture for TestClient"""
        return TestClient(app)

    @pytest.fixture
    def test_users(self) -> List[Dict]:
        """Fixture for multiple test user credentials"""
        return [
            {
                "email": f"test_group_expense_{i}@example.com",
                "password": "testpassword123",
                "full_name": f"Test Group Expense User {i}"
            } for i in range(3)  # Create 3 test users
        ]

    @pytest.fixture(autouse=True)
    def setup_test_users(self, client, test_users):
        """Create test users if they don't exist"""
        for user in test_users:
            response = client.post("/users/", json=user)
            if response.status_code not in (200, 400):  # 400 means user exists
                pytest.fail(f"Failed to setup test user: {response.text}")

    @pytest.fixture
    def auth_headers_list(self, client, test_users) -> List[Dict]:
        """Fixture for authorization headers for all users"""
        headers_list = []
        for user in test_users:
            response = client.post(
                "/token",
                data={
                    "username": user["email"],
                    "password": user["password"],
                    "grant_type": "password"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            assert response.status_code == 200, f"Failed to get auth token for {user['email']}"
            token = response.json()["access_token"]
            headers_list.append({
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            })
        return headers_list

    @pytest.fixture
    def test_group(self) -> Dict:
        """Fixture for test group data"""
        return {
            "name": "Test Expense Group"
        }

    @pytest.fixture
    def created_group(self, client, auth_headers_list, test_group) -> Dict:
        """Fixture to create a test group and add all users to it"""
        # Create group with first user
        response = client.post(
            "/groups/",
            json=test_group,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 200
        group_data = response.json()

        # Add other users to the group
        for headers in auth_headers_list[1:]:
            join_response = client.post(
                f"/groups/{group_data['id']}/join",
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
    def valid_custom_split_expense(self) -> Dict:
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
        self, client, auth_headers_list, created_group, valid_equal_split_expense
    ):
        """Test successful creation of equally split expense"""
        response = client.post(
            f"/groups/{created_group['id']}/expenses",
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
        self, client, auth_headers_list, created_group, valid_custom_split_expense
    ):
        """Test successful creation of custom split expense"""
        response = client.post(
            f"/groups/{created_group['id']}/expenses",
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

    def test_create_expense_unauthorized(
        self, client, created_group, valid_equal_split_expense
    ):
        """Test expense creation without authorization"""
        response = client.post(
            f"/groups/{created_group['id']}/expenses",
            json=valid_equal_split_expense
        )
        assert response.status_code == 401

    def test_create_expense_invalid_group(
        self, client, auth_headers_list, valid_equal_split_expense
    ):
        """Test creating expense for non-existent group"""
        response = client.post(
            "/groups/99999/expenses",
            json=valid_equal_split_expense,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 404

    def test_create_expense_negative_amount(
        self, client, auth_headers_list, created_group, valid_equal_split_expense
    ):
        """Test expense creation with negative amount"""
        valid_equal_split_expense["amount"] = -100.00
        response = client.post(
            f"/groups/{created_group['id']}/expenses",
            json=valid_equal_split_expense,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 422

    def test_create_custom_split_invalid_percentages(
        self, client, auth_headers_list, created_group, valid_custom_split_expense
    ):
        """Test custom split with invalid percentage total"""
        valid_custom_split_expense["custom_splits"] = {
            "1": 60,  # Total > 100%
            "2": 30,
            "3": 20
        }
        response = client.post(
            f"/groups/{created_group['id']}/expenses",
            json=valid_custom_split_expense,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 400

    def test_create_custom_split_missing_users(
        self, client, auth_headers_list, created_group, valid_custom_split_expense
    ):
        """Test custom split with missing users"""
        valid_custom_split_expense["custom_splits"] = {
            "1": 70,  # Missing user 3
            "2": 30
        }
        response = client.post(
            f"/groups/{created_group['id']}/expenses",
            json=valid_custom_split_expense,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 200

    @pytest.mark.parametrize("field", ["date", "category", "amount"])
    def test_create_expense_missing_required_fields(
        self, client, auth_headers_list, created_group, valid_equal_split_expense, field
    ):
        """Test expense creation with missing required fields"""
        invalid_expense = valid_equal_split_expense.copy()
        del invalid_expense[field]
        response = client.post(
            f"/groups/{created_group['id']}/expenses",
            json=invalid_expense,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 422

    def test_create_expense_invalid_split_type(
        self, client, auth_headers_list, created_group, valid_equal_split_expense
    ):
        """Test expense creation with invalid split type"""
        valid_equal_split_expense["split_type"] = "invalid_type"
        response = client.post(
            f"/groups/{created_group['id']}/expenses",
            json=valid_equal_split_expense,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 400

    def test_create_custom_split_zero_percentage(
        self, client, auth_headers_list, created_group, valid_custom_split_expense
    ):
        """Test custom split with zero percentage"""
        valid_custom_split_expense["custom_splits"] = {
            "1": 0,    # Invalid: zero percentage
            "2": 50,
            "3": 50
        }
        response = client.post(
            f"/groups/{created_group['id']}/expenses",
            json=valid_custom_split_expense,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 200

    def test_create_expense_future_date(
        self, client, auth_headers_list, created_group, valid_equal_split_expense
    ):
        """Test expense creation with future date"""
        future_date = datetime(2025, 12, 31, 12, 0, tzinfo=timezone.utc).isoformat()
        valid_equal_split_expense["date"] = future_date
        response = client.post(
            f"/groups/{created_group['id']}/expenses",
            json=valid_equal_split_expense,
            headers=auth_headers_list[0]
        )
        assert response.status_code == 200

    def test_create_expense_non_member(
        self, client, created_group, valid_equal_split_expense
    ):
        """Test expense creation by non-group member"""
        # Create a new user who is not a member of the group
        new_user = {
            "email": "non_member@example.com",
            "password": "testpassword123",
            "full_name": "Non Member User"
        }
        client.post("/users/", json=new_user)
        token_response = client.post(
            "/token",
            data={
                "username": new_user["email"],
                "password": new_user["password"],
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        non_member_headers = {
            "Authorization": f"Bearer {token_response.json()['access_token']}",
            "Content-Type": "application/json"
        }

        response = client.post(
            f"/groups/{created_group['id']}/expenses",
            json=valid_equal_split_expense,
            headers=non_member_headers
        )
        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--disable-warnings"])
