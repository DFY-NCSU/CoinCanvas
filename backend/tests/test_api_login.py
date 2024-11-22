import pytest
import requests
import logging
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://127.0.0.1:8000"


class TestLogin:
    """Test token-related endpoints"""

    @pytest.fixture
    def test_user(self) -> Dict:
        """Fixture for test user credentials"""
        return {
            "email": "test_token@example.com",
            "password": "testpassword123",
            "full_name": "Test Token User"
        }

    @pytest.fixture(autouse=True)
    def setup_test_user(self, test_user):
        """Create test user if doesn't exist"""
        response = requests.post(f"{BASE_URL}/users/", json=test_user)
        if response.status_code not in (200, 400):  # 400 means user exists
            pytest.fail(f"Failed to setup test user: {response.text}")

    def test_successful_token_generation(self, test_user):
        """Test successful token generation with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/token",
            data={
                "username": test_user["email"],
                "password": test_user["password"],
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_invalid_password(self, test_user):
        """Test token generation with invalid password"""
        response = requests.post(
            f"{BASE_URL}/token",
            data={
                "username": test_user["email"],
                "password": "wrongpassword",
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401

    def test_invalid_username(self, test_user):
        """Test token generation with invalid username"""
        response = requests.post(
            f"{BASE_URL}/token",
            data={
                "username": "nonexistent@example.com",
                "password": test_user["password"],
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401

    def test_missing_username(self, test_user):
        """Test token generation with missing username"""
        response = requests.post(
            f"{BASE_URL}/token",
            data={
                "password": test_user["password"],
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 422

    def test_missing_password(self, test_user):
        """Test token generation with missing password"""
        response = requests.post(
            f"{BASE_URL}/token",
            data={
                "username": test_user["email"],
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 422

    def test_empty_username(self, test_user):
        """Test token generation with empty username"""
        response = requests.post(
            f"{BASE_URL}/token",
            data={
                "username": "",
                "password": test_user["password"],
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 422

    def test_empty_password(self, test_user):
        """Test token generation with empty password"""
        response = requests.post(
            f"{BASE_URL}/token",
            data={
                "username": test_user["email"],
                "password": "",
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 422

    def test_invalid_grant_type(self, test_user):
        """Test token generation with invalid grant type"""
        response = requests.post(
            f"{BASE_URL}/token",
            data={
                "username": test_user["email"],
                "password": test_user["password"],
                "grant_type": "invalid"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 422

    def test_optional_scope(self, test_user):
        """Test token generation with optional scope parameter"""
        response = requests.post(
            f"{BASE_URL}/token",
            data={
                "username": test_user["email"],
                "password": test_user["password"],
                "grant_type": "password",
                "scope": "read write"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_optional_client_credentials(self, test_user):
        """Test token generation with optional client credentials"""
        response = requests.post(
            f"{BASE_URL}/token",
            data={
                "username": test_user["email"],
                "password": test_user["password"],
                "grant_type": "password",
                "client_id": "test_client",
                "client_secret": "test_secret"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code in (200, 422)  # Depending on if client auth is implemented

    def test_wrong_content_type(self, test_user):
        """Test token generation with wrong content type"""
        response = requests.post(
            f"{BASE_URL}/token",
            json={  # Using JSON instead of form data
                "username": test_user["email"],
                "password": test_user["password"],
                "grant_type": "password"
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_token_format(self, test_user):
        """Test the format of the generated token"""
        response = requests.post(
            f"{BASE_URL}/token",
            data={
                "username": test_user["email"],
                "password": test_user["password"],
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert "access_token" in data
        assert "token_type" in data

        # Check data types
        assert isinstance(data["access_token"], str)
        assert isinstance(data["token_type"], str)

        # Check token format (assuming JWT)
        assert len(data["access_token"].split('.')) == 3

        # Check token type
        assert data["token_type"].lower() == "bearer"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--disable-warnings"])
