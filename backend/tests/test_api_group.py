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


class TestGroupOperations:
    """Test group-related endpoints"""

    @pytest.fixture
    def test_user(self) -> Dict:
        """Fixture for test user credentials"""
        return {
            "email": f"test_group_{time.time()}@example.com",
            "password": "testpassword123",
            "full_name": "Test Group User"
        }

    @pytest.fixture
    def second_test_user(self) -> Dict:
        """Fixture for second test user credentials"""
        return {
            "email": f"test_group_second_{time.time()}@example.com",
            "password": "testpassword123",
            "full_name": "Second Test Group User"
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
    def second_auth_token(self, second_test_user) -> str:
        """Fixture to create second user and get auth token"""
        # Create second test user
        requests.post(f"{BASE_URL}/users/", json=second_test_user)

        # Get token
        response = requests.post(
            f"{BASE_URL}/token",
            data={
                "username": second_test_user["email"],
                "password": second_test_user["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200, "Failed to get second auth token"
        return response.json()["access_token"]

    @pytest.fixture
    def auth_headers(self, auth_token) -> Dict:
        """Fixture for authorization headers"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

    @pytest.fixture
    def second_auth_headers(self, second_auth_token) -> Dict:
        """Fixture for second user's authorization headers"""
        return {
            "Authorization": f"Bearer {second_auth_token}",
            "Content-Type": "application/json"
        }

    @pytest.fixture
    def valid_group(self) -> Dict:
        """Fixture for valid group data"""
        return {
            "name": f"Test Group {time.time()}"
        }

    def test_create_group_success(self, auth_headers, valid_group):
        """Test successful group creation"""
        response = requests.post(
            f"{BASE_URL}/groups/",
            json=valid_group,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == valid_group["name"]
        assert "id" in data
        assert "created_by" in data

    def test_create_group_unauthorized(self, valid_group):
        """Test group creation without authorization"""
        response = requests.post(
            f"{BASE_URL}/groups/",
            json=valid_group
        )
        assert response.status_code == 401

    def test_create_group_invalid_token(self, valid_group):
        """Test group creation with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.post(
            f"{BASE_URL}/groups/",
            json=valid_group,
            headers=headers
        )
        assert response.status_code == 401

    def test_create_group_empty_name(self, auth_headers):
        """Test group creation with empty name"""
        invalid_group = {"name": ""}
        response = requests.post(
            f"{BASE_URL}/groups/",
            json=invalid_group,
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_create_group_long_name(self, auth_headers):
        """Test group creation with very long name"""
        invalid_group = {"name": "a" * 1000}
        response = requests.post(
            f"{BASE_URL}/groups/",
            json=invalid_group,
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_join_group_success(self, auth_headers, second_auth_headers, valid_group):
        """Test successful group joining"""
        # First create a group
        create_response = requests.post(
            f"{BASE_URL}/groups/",
            json=valid_group,
            headers=auth_headers
        )
        group_id = create_response.json()["id"]

        # Second user tries to join the group
        join_response = requests.post(
            f"{BASE_URL}/groups/{group_id}/join",
            headers=second_auth_headers
        )
        assert join_response.status_code == 200

    def test_join_group_unauthorized(self, auth_headers, valid_group):
        """Test joining group without authorization"""
        # First create a group
        create_response = requests.post(
            f"{BASE_URL}/groups/",
            json=valid_group,
            headers=auth_headers
        )
        group_id = create_response.json()["id"]

        # Try to join without authorization
        response = requests.post(
            f"{BASE_URL}/groups/{group_id}/join"
        )
        assert response.status_code == 401

    def test_join_nonexistent_group(self, auth_headers):
        """Test joining a group that doesn't exist"""
        response = requests.post(
            f"{BASE_URL}/groups/99999/join",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_join_group_twice(self, auth_headers, valid_group):
        """Test joining the same group twice"""
        # First create a group
        create_response = requests.post(
            f"{BASE_URL}/groups/",
            json=valid_group,
            headers=auth_headers
        )
        group_id = create_response.json()["id"]

        # Try to join the group again (creator is already a member)
        response = requests.post(
            f"{BASE_URL}/groups/{group_id}/join",
            headers=auth_headers
        )
        assert response.status_code == 400

    def test_get_user_groups_success(self, auth_headers, valid_group):
        """Test successfully getting user's groups"""
        # First create a group
        requests.post(
            f"{BASE_URL}/groups/",
            json=valid_group,
            headers=auth_headers
        )

        # Get user's groups
        response = requests.get(
            f"{BASE_URL}/groups/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["name"] == valid_group["name"]

    def test_get_user_groups_unauthorized(self):
        """Test getting user's groups without authorization"""
        response = requests.get(f"{BASE_URL}/groups/")
        assert response.status_code == 401

    def test_get_user_groups_invalid_token(self):
        """Test getting user's groups with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(
            f"{BASE_URL}/groups/",
            headers=headers
        )
        assert response.status_code == 401

    def test_get_user_groups_pagination(self, auth_headers):
        """Test pagination of user's groups"""
        response = requests.get(
            f"{BASE_URL}/groups/?skip=0&limit=5",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_get_user_groups_empty(self, second_auth_headers):
        """Test getting groups for user with no groups"""
        response = requests.get(
            f"{BASE_URL}/groups/",
            headers=second_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--disable-warnings"])
