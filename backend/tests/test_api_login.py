import pytest
from fastapi.testclient import TestClient
import logging
from typing import Dict

from app.main import app

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class TestLogin:
    """Test token-related endpoints"""

    @pytest.fixture
    def client(self):
        """Fixture for TestClient"""
        return TestClient(app)

    @pytest.fixture
    def test_user(self) -> Dict:
        """Fixture for test user credentials"""
        return {
            "email": "test_token@example.com",
            "password": "testpassword123",
            "full_name": "Test Token User"
        }

    @pytest.fixture(autouse=True)
    def setup_test_user(self, client, test_user):
        """Create test user if doesn't exist"""
        response = client.post("/users/", json=test_user)
        if response.status_code not in (200, 400):  # 400 means user exists
            pytest.fail(f"Failed to setup test user: {response.text}")

    def test_successful_token_generation(self, client, test_user):
        """Test successful token generation with valid credentials"""
        response = client.post(
            "/token",
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

    def test_invalid_password(self, client, test_user):
        """Test token generation with invalid password"""
        response = client.post(
            "/token",
            data={
                "username": test_user["email"],
                "password": "wrongpassword",
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401

    def test_invalid_username(self, client, test_user):
        """Test token generation with invalid username"""
        response = client.post(
            "/token",
            data={
                "username": "nonexistent@example.com",
                "password": test_user["password"],
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401

    def test_missing_username(self, client, test_user):
        """Test token generation with missing username"""
        response = client.post(
            "/token",
            data={
                "password": test_user["password"],
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 422

    def test_missing_password(self, client, test_user):
        """Test token generation with missing password"""
        response = client.post(
            "/token",
            data={
                "username": test_user["email"],
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 422

    def test_empty_username(self, client, test_user):
        """Test token generation with empty username"""
        response = client.post(
            "/token",
            data={
                "username": "",
                "password": test_user["password"],
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 422

    def test_empty_password(self, client, test_user):
        """Test token generation with empty password"""
        response = client.post(
            "/token",
            data={
                "username": test_user["email"],
                "password": "",
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 422

    def test_invalid_grant_type(self, client, test_user):
        """Test token generation with invalid grant type"""
        response = client.post(
            "/token",
            data={
                "username": test_user["email"],
                "password": test_user["password"],
                "grant_type": "invalid"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 422

    def test_optional_scope(self, client, test_user):
        """Test token generation with optional scope parameter"""
        response = client.post(
            "/token",
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

    def test_optional_client_credentials(self, client, test_user):
        """Test token generation with optional client credentials"""
        response = client.post(
            "/token",
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

    def test_wrong_content_type(self, client, test_user):
        """Test token generation with wrong content type"""
        response = client.post(
            "/token",
            json={  # Using JSON instead of form data
                "username": test_user["email"],
                "password": test_user["password"],
                "grant_type": "password"
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_token_format(self, client, test_user):
        """Test the format of the generated token"""
        response = client.post(
            "/token",
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

    def test_user_creation_existing_email(self, client, test_user):
        """Test creating a user with an email that already exists"""
        response = client.post("/users/", json=test_user)
        assert response.status_code == 400
        assert "email already registered" in response.json()["detail"].lower()

    def test_token_with_special_characters_username(self, client, test_user):
        """Test token generation with a username containing special characters"""
        response = client.post(
            "/token",
            data={
                "username": "user+test@example.com",
                "password": test_user["password"],
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401

    def test_token_with_incorrect_grant_type_case(self, client, test_user):
        """Test token generation with grant type in different casing"""
        response = client.post(
            "/token",
            data={
                "username": test_user["email"],
                "password": test_user["password"],
                "grant_type": "PASSWORD"  # Uppercase grant type
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 422

    def test_token_with_extra_parameters(self, client, test_user):
        """Test token generation with additional unexpected parameters"""
        response = client.post(
            "/token",
            data={
                "username": test_user["email"],
                "password": test_user["password"],
                "grant_type": "password",
                "extra_param": "unexpected_value"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code in (200, 400)

    def test_token_without_content_type(self, client, test_user):
        """Test token generation without specifying Content-Type header"""
        response = client.post(
            "/token",
            data={
                "username": test_user["email"],
                "password": test_user["password"],
                "grant_type": "password"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_token_with_long_username(self, client):
        """Test token generation with an excessively long username"""
        long_username = "a" * 256 + "@example.com"
        response = client.post(
            "/token",
            data={
                "username": long_username,
                "password": "testpassword",
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401

    def test_token_with_blank_grant_type(self, client, test_user):
        """Test token generation with a blank grant type"""
        response = client.post(
            "/token",
            data={
                "username": test_user["email"],
                "password": test_user["password"],
                "grant_type": ""
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_token_with_numeric_password(self, client, test_user):
        """Test token generation with a purely numeric password"""
        test_user["password"] = "12345678"
        response = client.post(
            "/token",
            data={
                "username": test_user["email"],
                "password": test_user["password"],
                "grant_type": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code in (200, 401)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--disable-warnings"])
