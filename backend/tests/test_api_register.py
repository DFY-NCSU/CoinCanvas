import pytest
import requests
import logging
import time
from typing import Dict, Tuple

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://127.0.0.1:8000"

class TestRegister:
    """Test user-related endpoints"""
    
    @pytest.fixture
    def test_user(self) -> Dict:
        return {
            "email": f"test{time.time()}@example.com",  # Dynamic email to avoid conflicts
            "full_name": "name",
            "password": "pass"
        }
    
    @pytest.fixture
    def created_user_response(self, test_user) -> Tuple[requests.Response, Dict]:
        """Fixture to create user and return both response and data"""
        response = requests.post(
            f"{BASE_URL}/users/",
            json=test_user
        )
        return response, response.json() if response.status_code == 200 else {}

    def test_successful_user_creation(self, test_user):
        """Test if user creation succeeds with valid data"""
        response = requests.post(f"{BASE_URL}/users/", json=test_user)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert data["email"] == test_user["email"]

    def test_duplicate_user_creation(self, test_user):
        """Test duplicate user creation"""
        # First creation
        first_response = requests.post(f"{BASE_URL}/users/", json=test_user)
        assert first_response.status_code == 200
        
        # Second creation
        second_response = requests.post(f"{BASE_URL}/users/", json=test_user)
        assert second_response.status_code == 400
        assert "Email already registered" in second_response.text

    # Input validation tests - updated status codes to 422
    @pytest.mark.parametrize("invalid_email", [
        "",
        "notanemail",
        "@example.com",
        "user@",
        "user@.com",
        "user@example."
    ])
    def test_invalid_email_formats(self, test_user, invalid_email):
        """Test various invalid email formats"""
        invalid_user = test_user.copy()
        invalid_user["email"] = invalid_email
        response = requests.post(f"{BASE_URL}/users/", json=invalid_user)
        assert response.status_code == 422
        
    def test_missing_email(self, test_user):
        """Test user creation with missing email"""
        invalid_user = test_user.copy()
        del invalid_user["email"]
        response = requests.post(f"{BASE_URL}/users/", json=invalid_user)
        assert response.status_code == 422

    def test_missing_password(self, test_user):
        """Test user creation with missing password"""
        invalid_user = test_user.copy()
        del invalid_user["password"]
        response = requests.post(f"{BASE_URL}/users/", json=invalid_user)
        assert response.status_code == 422

    def test_missing_full_name(self, test_user):
        """Test user creation with missing full name"""
        invalid_user = test_user.copy()
        del invalid_user["full_name"]
        response = requests.post(f"{BASE_URL}/users/", json=invalid_user)
        assert response.status_code == 422

    def test_empty_password(self, test_user):
        """Test user creation with empty password"""
        invalid_user = test_user.copy()
        invalid_user["password"] = ""
        response = requests.post(f"{BASE_URL}/users/", json=invalid_user)
        assert response.status_code == 422

    def test_empty_full_name(self, test_user):
        """Test user creation with empty full name"""
        invalid_user = test_user.copy()
        invalid_user["full_name"] = ""
        response = requests.post(f"{BASE_URL}/users/", json=invalid_user)
        assert response.status_code == 422

    def test_response_format_success(self, test_user):
        """Test successful response format"""
        response = requests.post(f"{BASE_URL}/users/", json=test_user)
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

    def test_validation_error_format(self, test_user):
        """Test validation error response format"""
        invalid_user = test_user.copy()
        invalid_user["email"] = "invalid-email"
        response = requests.post(f"{BASE_URL}/users/", json=invalid_user)
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

    def test_special_characters_in_name(self, test_user):
        """Test full name with special characters"""
        test_user["full_name"] = "O'Connor-Smith"
        response = requests.post(f"{BASE_URL}/users/", json=test_user)
        assert response.status_code == 200

    def test_long_values(self, test_user):
        """Test with long input values"""
        test_user["full_name"] = "a" * 100
        response = requests.post(f"{BASE_URL}/users/", json=test_user)
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])