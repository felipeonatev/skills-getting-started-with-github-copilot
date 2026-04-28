"""
Tests for the Mergington High School API
Using AAA (Arrange-Act-Assert) testing pattern
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture providing a test client for the FastAPI app"""
    return TestClient(app)


class TestActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_activities_returns_success(self, client):
        """Test that GET /activities returns a 200 status code"""
        # Arrange - nothing to set up
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        # Arrange - nothing to set up
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert isinstance(activities, dict)
        assert len(activities) > 0

    def test_get_activities_contains_required_fields(self, client):
        """Test that each activity contains all required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"

    def test_get_activities_participants_is_list(self, client):
        """Test that participants field is a list"""
        # Arrange - nothing to set up
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"Activity '{activity_name}' participants should be a list"


class TestSignup:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client):
        """Test successful student signup"""
        # Arrange
        test_email = "testStudent@test.com"
        activity_name = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert test_email in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant"""
        # Arrange
        test_email = "newStudent@test.com"
        activity_name = "Chess Club"
        
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        response = client.get("/activities")
        updated_count = len(response.json()[activity_name]["participants"])
        assert updated_count == initial_count + 1
        assert test_email in response.json()[activity_name]["participants"]

    def test_signup_duplicate_returns_400(self, client):
        """Test that duplicate signup returns 400 error"""
        # Arrange
        test_email = "duplicate@test.com"
        activity_name = "Gym Class"
        
        # Act - First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert - First signup succeeds
        assert response1.status_code == 200
        
        # Act - Second signup with same email
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert - Second signup fails
        assert response2.status_code == 400
        data = response2.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signup to non-existent activity returns 404"""
        # Arrange
        test_email = "student@test.com"
        fake_activity = "Fake Activity"
        
        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_correct_activity(self, client):
        """Test that signup adds participant to the correct activity"""
        # Arrange
        test_email = "correctActivity@test.com"
        target_activity = "Programming Class"
        
        # Act
        client.post(
            f"/activities/{target_activity}/signup",
            params={"email": test_email}
        )
        
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert test_email in activities[target_activity]["participants"]
        
        # Verify not in other activities
        for activity_name, activity_data in activities.items():
            if activity_name != target_activity:
                assert test_email not in activity_data["participants"]

    def test_signup_with_special_characters_in_email(self, client):
        """Test signup with special characters in email"""
        # Arrange
        test_email = "user+test@example.com"
        activity_name = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert - Signup succeeds
        assert response.status_code == 200
        
        # Verify it was added
        response = client.get("/activities")
        activities = response.json()
        assert test_email in activities[activity_name]["participants"]
