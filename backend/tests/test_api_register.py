import pytest
from fastapi.testclient import TestClient
import logging
from typing import Dict, Tuple

from app.main import app

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class TestRegister:
    """Test user-related endpoints"""

    @pytest.fixture
    def client(self):
        """Fixture for TestClient"""
        return TestClient(app)

    @pytest.fixture
    def test_user(self) -> Dict:
        import time
        return {
            "email": f"test_{time.time()}@example.com",
            "full_name": "name",
            "password": "pass"
        }

    @pytest.fixture
    def created_user_response(self, client, test_user) -> Tuple[int, Dict]:
        """Fixture to create user and return both status code and data"""
        response = client.post("/users/", json=test_user)
        return response.status_code, response.json() if response.status_code == 200 else {}

    def test_successful_user_creation(self, client, test_user):
        """Test if user creation succeeds with valid data"""
        response = client.post("/users/", json=test_user)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert data["email"] == test_user["email"]

    def test_duplicate_user_creation(self, client, test_user):
        """Test duplicate user creation"""
        # First creation
        first_response = client.post("/users/", json=test_user)
        assert first_response.status_code == 200

        # Second creation
        second_response = client.post("/users/", json=test_user)
        assert second_response.status_code == 400
        assert "Email already registered" in second_response.text

    @pytest.mark.parametrize("invalid_email", [
        "",
        "notanemail",
        "@example.com",
        "user@",
        "user@.com",
        "user@example."
    ])
    def test_invalid_email_formats(self, client, test_user, invalid_email):
        """Test various invalid email formats"""
        invalid_user = test_user.copy()
        invalid_user["email"] = invalid_email
        response = client.post("/users/", json=invalid_user)
        assert response.status_code == 422

    def test_missing_email(self, client, test_user):
        """Test user creation with missing email"""
        invalid_user = test_user.copy()
        del invalid_user["email"]
        response = client.post("/users/", json=invalid_user)
        assert response.status_code == 422

    def test_missing_password(self, client, test_user):
        """Test user creation with missing password"""
        invalid_user = test_user.copy()
        del invalid_user["password"]
        response = client.post("/users/", json=invalid_user)
        assert response.status_code == 422

    def test_missing_full_name(self, client, test_user):
        """Test user creation with missing full name"""
        invalid_user = test_user.copy()
        del invalid_user["full_name"]
        response = client.post("/users/", json=invalid_user)
        assert response.status_code == 422

    def test_empty_password(self, client, test_user):
        """Test user creation with empty password"""
        invalid_user = test_user.copy()
        invalid_user["password"] = ""
        response = client.post("/users/", json=invalid_user)
        assert response.status_code == 422

    def test_empty_full_name(self, client, test_user):
        """Test user creation with empty full name"""
        invalid_user = test_user.copy()
        invalid_user["full_name"] = ""
        response = client.post("/users/", json=invalid_user)
        assert response.status_code == 422

    def test_response_format_success(self, client, test_user):
        """Test successful response format"""
        response = client.post("/users/", json=test_user)
        assert response.status_code == 200
        data = response.json()

        # Check required fields
        required_fields = ["email", "full_name", "id"]
        for field in required_fields:
            assert field in data

        # Verify data types
        assert isinstance(data["id"], int)
        assert isinstance(data["email"], str)
        assert isinstance(data["full_name"], str)

        # Verify values
        assert data["email"] == test_user["email"]
        assert data["full_name"] == test_user["full_name"]
        assert "password" not in data

    def test_validation_error_format(self, client, test_user):
        """Test validation error response format"""
        invalid_user = test_user.copy()
        invalid_user["email"] = "invalid-email"
        response = client.post("/users/", json=invalid_user)
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

    def test_special_characters_in_name(self, client, test_user):
        """Test full name with special characters"""
        test_user["full_name"] = "O'Connor-Smith"
        response = client.post("/users/", json=test_user)
        assert response.status_code == 200

    def test_long_values(self, client, test_user):
        """Test with long input values"""
        test_user["full_name"] = "a" * 100
        response = client.post("/users/", json=test_user)
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
