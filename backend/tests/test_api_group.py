import pytest
from fastapi.testclient import TestClient
import logging
from typing import Dict

from app.main import app

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class TestGroupOperations:
    """Test group-related endpoints"""

    @pytest.fixture
    def client(self):
        """Fixture for TestClient"""
        return TestClient(app)

    @pytest.fixture
    def test_user(self) -> Dict:
        """Fixture for test user credentials"""
        return {
            "email": "test_group@example.com",
            "password": "testpassword123",
            "full_name": "Test Group User"
        }

    @pytest.fixture
    def second_test_user(self) -> Dict:
        """Fixture for second test user credentials"""
        import time
        return {
            "email": f"test_group_second_{time.time()}@example.com",
            "password": "testpassword123",
            "full_name": "Second Test Group User"
        }

    @pytest.fixture(autouse=True)
    def setup_test_users(self, client, test_user, second_test_user):
        """Create test users if they don't exist"""
        for user in [test_user, second_test_user]:
            response = client.post("/users/", json=user)
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
    def second_auth_headers(self, client, second_test_user) -> Dict:
        """Fixture for second user's authorization headers"""
        response = client.post(
            "/token",
            data={
                "username": second_test_user["email"],
                "password": second_test_user["password"],
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200, "Failed to get second auth token"
        token = response.json()["access_token"]
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    @pytest.fixture
    def valid_group(self) -> Dict:
        """Fixture for valid group data"""
        return {
            "name": "Test Group"
        }

    def test_create_group_success(self, client, auth_headers, valid_group):
        """Test successful group creation"""
        response = client.post("/groups/", json=valid_group, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == valid_group["name"]
        assert "id" in data
        assert "created_by" in data

    def test_create_group_unauthorized(self, client, valid_group):
        """Test group creation without authorization"""
        response = client.post("/groups/", json=valid_group)
        assert response.status_code == 401

    def test_create_group_invalid_token(self, client, valid_group):
        """Test group creation with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/groups/", json=valid_group, headers=headers)
        assert response.status_code == 401

    def test_create_group_empty_name(self, client, auth_headers):
        """Test group creation with empty name"""
        invalid_group = {"name": ""}
        response = client.post("/groups/", json=invalid_group, headers=auth_headers)
        assert response.status_code == 422

    def test_create_group_long_name(self, client, auth_headers):
        """Test group creation with very long name"""
        invalid_group = {"name": "a" * 1000}
        response = client.post("/groups/", json=invalid_group, headers=auth_headers)
        assert response.status_code == 200

    def test_join_group_success(self, client, auth_headers, second_auth_headers, valid_group):
        """Test successful group joining"""
        # First create a group
        create_response = client.post("/groups/", json=valid_group, headers=auth_headers)
        group_id = create_response.json()["id"]

        # Second user tries to join the group
        join_response = client.post(
            f"/groups/{group_id}/join",
            headers=second_auth_headers
        )
        assert join_response.status_code == 200

    def test_join_group_unauthorized(self, client, auth_headers, valid_group):
        """Test joining group without authorization"""
        # First create a group
        create_response = client.post("/groups/", json=valid_group, headers=auth_headers)
        group_id = create_response.json()["id"]

        # Try to join without authorization
        response = client.post(f"/groups/{group_id}/join")
        assert response.status_code == 401

    def test_join_nonexistent_group(self, client, auth_headers):
        """Test joining a group that doesn't exist"""
        response = client.post("/groups/99999/join", headers=auth_headers)
        assert response.status_code == 404

    def test_join_group_twice(self, client, auth_headers, valid_group):
        """Test joining the same group twice"""
        # First create a group
        create_response = client.post("/groups/", json=valid_group, headers=auth_headers)
        group_id = create_response.json()["id"]

        # Try to join the group again (creator is already a member)
        response = client.post(f"/groups/{group_id}/join", headers=auth_headers)
        assert response.status_code == 400

    def test_get_user_groups_success(self, client, auth_headers, valid_group):
        """Test successfully getting user's groups"""
        # First create a group
        client.post("/groups/", json=valid_group, headers=auth_headers)

        # Get user's groups
        response = client.get("/groups/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["name"] == valid_group["name"]

    def test_get_user_groups_unauthorized(self, client):
        """Test getting user's groups without authorization"""
        response = client.get("/groups/")
        assert response.status_code == 401

    def test_get_user_groups_invalid_token(self, client):
        """Test getting user's groups with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/groups/", headers=headers)
        assert response.status_code == 401

    def test_get_user_groups_pagination(self, client, auth_headers):
        """Test pagination of user's groups"""
        response = client.get("/groups/?skip=0&limit=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_get_user_groups_empty(self, client, second_auth_headers):
        """Test getting groups for user with no groups"""
        response = client.get("/groups/", headers=second_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--disable-warnings"])
