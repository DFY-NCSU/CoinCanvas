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


class TestDeleteGroupExpenses:
    """Test deleting group expenses endpoints"""

    @pytest.fixture
    def test_users(self) -> List[Dict]:
        """Fixture for multiple test user credentials"""
        return [
            {
                "email": f"test_delete_expense_{i}_{time.time()}@example.com",
                "password": "testpassword123",
                "full_name": f"Test Delete Expense User {i}"
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
            "name": f"Test Delete Expense Group {time.time()}"
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
    def test_expense(self) -> Dict:
        """Fixture for test expense data"""
        return {
            "date": datetime.now(timezone.utc).isoformat(),
            "category": "Test Expense",
            "amount": 150.00,
            "description": "Test expense for deletion",
            "split_type": "equal"
        }

    @pytest.fixture
    def created_expense(
        self, auth_headers_list, created_group, test_expense
    ) -> Dict:
        """Fixture to create a test expense"""
        response = requests.post(
            f"{BASE_URL}/groups/{created_group['id']}/expenses",
            json=test_expense,
            headers=auth_headers_list[0]  # Created by first user
        )
        assert response.status_code == 200
        return response.json()

    def test_delete_expense_success_by_creator(
        self, auth_headers_list, created_group, created_expense
    ):
        """Test successful deletion of expense by its creator"""
        response = requests.delete(
            f"{BASE_URL}/groups/{created_group['id']}/expenses/{created_expense['id']}",
            headers=auth_headers_list[0]  # First user (creator)
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Expense deleted successfully"

        # Verify expense is actually deleted
        get_response = requests.get(
            f"{BASE_URL}/groups/{created_group['id']}/expenses/",
            headers=auth_headers_list[0]
        )
        expenses = get_response.json()
        expense_ids = [exp["id"] for exp in expenses]
        assert created_expense["id"] not in expense_ids

    def test_delete_expense_unauthorized(
        self, created_group, created_expense
    ):
        """Test expense deletion without authorization"""
        response = requests.delete(
            f"{BASE_URL}/groups/{created_group['id']}/expenses/{created_expense['id']}"
        )
        assert response.status_code == 401

    def test_delete_expense_by_non_creator(
        self, auth_headers_list, created_group, created_expense
    ):
        """Test deletion attempt by group member who didn't create the expense"""
        response = requests.delete(
            f"{BASE_URL}/groups/{created_group['id']}/expenses/{created_expense['id']}",
            headers=auth_headers_list[1]  # Second user (non-creator)
        )
        assert response.status_code == 403

    def test_delete_expense_invalid_group(
        self, auth_headers_list, created_expense
    ):
        """Test deletion with invalid group ID"""
        response = requests.delete(
            f"{BASE_URL}/groups/99999/expenses/{created_expense['id']}",
            headers=auth_headers_list[0]
        )
        assert response.status_code == 404

    def test_delete_expense_invalid_expense(
        self, auth_headers_list, created_group
    ):
        """Test deletion with invalid expense ID"""
        response = requests.delete(
            f"{BASE_URL}/groups/{created_group['id']}/expenses/99999",
            headers=auth_headers_list[0]
        )
        assert response.status_code == 404

    def test_delete_expense_by_group_admin(
        self, auth_headers_list, created_group, test_expense
    ):
        """Test deletion of expense by group admin (even if not creator)"""
        # Create expense with second user
        response = requests.post(
            f"{BASE_URL}/groups/{created_group['id']}/expenses",
            json=test_expense,
            headers=auth_headers_list[1]
        )
        expense = response.json()

        # Delete expense with first user (group admin)
        response = requests.delete(
            f"{BASE_URL}/groups/{created_group['id']}/expenses/{expense['id']}",
            headers=auth_headers_list[0]
        )
        assert response.status_code == 200

    def test_delete_expense_non_member(
        self, created_group, created_expense
    ):
        """Test deletion attempt by non-group member"""
        # Create a new user who is not a member of the group
        new_user = {
            "email": f"non_member_delete_{time.time()}@example.com",
            "password": "testpassword123",
            "full_name": "Non Member Delete User"
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

        response = requests.delete(
            f"{BASE_URL}/groups/{created_group['id']}/expenses/{created_expense['id']}",
            headers=non_member_headers
        )
        assert response.status_code == 403

    def test_delete_expense_already_deleted(
        self, auth_headers_list, created_group, created_expense
    ):
        """Test deleting an already deleted expense"""
        # Delete expense first time
        requests.delete(
            f"{BASE_URL}/groups/{created_group['id']}/expenses/{created_expense['id']}",
            headers=auth_headers_list[0]
        )

        # Try to delete again
        response = requests.delete(
            f"{BASE_URL}/groups/{created_group['id']}/expenses/{created_expense['id']}",
            headers=auth_headers_list[0]
        )
        assert response.status_code == 404

    def test_delete_multiple_expenses(
        self, auth_headers_list, created_group, test_expense
    ):
        """Test deleting multiple expenses in sequence"""
        created_expenses = []
        # Create multiple expenses
        for i in range(3):
            expense = test_expense.copy()
            expense["description"] = f"Test expense {i}"
            response = requests.post(
                f"{BASE_URL}/groups/{created_group['id']}/expenses",
                json=expense,
                headers=auth_headers_list[0]
            )
            created_expenses.append(response.json())

        # Delete each expense
        for expense in created_expenses:
            response = requests.delete(
                f"{BASE_URL}/groups/{created_group['id']}/expenses/{expense['id']}",
                headers=auth_headers_list[0]
            )
            assert response.status_code == 200

        # Verify all expenses are deleted
        get_response = requests.get(
            f"{BASE_URL}/groups/{created_group['id']}/expenses/",
            headers=auth_headers_list[0]
        )
        remaining_expenses = get_response.json()
        for expense in created_expenses:
            assert expense["id"] not in [exp["id"] for exp in remaining_expenses]

    def test_delete_expense_expired_token(
        self, created_group, created_expense
    ):
        """Test deleting expense with expired token"""
        headers = {
            "Authorization": "Bearer expired.token.here",
            "Content-Type": "application/json"
        }
        response = requests.delete(
            f"{BASE_URL}/groups/{created_group['id']}/expenses/{created_expense['id']}",
            headers=headers
        )
        assert response.status_code == 401

    def test_delete_expense_verify_splits_deleted(
        self, auth_headers_list, created_group, created_expense
    ):
        """Test that expense splits are deleted when expense is deleted"""
        # Delete the expense
        response = requests.delete(
            f"{BASE_URL}/groups/{created_group['id']}/expenses/{created_expense['id']}",
            headers=auth_headers_list[0]
        )
        assert response.status_code == 200

        # Verify the expense and its splits are deleted by trying to get the expense
        get_response = requests.get(
            f"{BASE_URL}/groups/{created_group['id']}/expenses/",
            headers=auth_headers_list[0]
        )
        expenses = get_response.json()
        deleted_expense = next(
            (exp for exp in expenses if exp["id"] == created_expense["id"]),
            None
        )
        assert deleted_expense is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--disable-warnings"])
