"""
Tests for the High School Management System API

Tests follow the Arrange-Act-Assert (AAA) pattern:
- Arrange: Set up test data and expected values
- Act: Execute the operation being tested
- Assert: Verify the results
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


def test_get_activities_returns_activities():
    """Test that GET /activities returns all activities"""
    # Arrange - expect the response to contain activities
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert len(data) > 0


def test_activity_has_required_fields():
    """Test that activities contain required fields"""
    # Arrange - expected fields in activity data
    expected_fields = {"description", "schedule", "max_participants", "participants"}
    
    # Act
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    for activity_name, activity_data in activities.items():
        assert set(activity_data.keys()) == expected_fields
        assert isinstance(activity_data["participants"], list)
        assert isinstance(activity_data["max_participants"], int)


def test_signup_for_activity_adds_participant():
    """Test that POST /activities/{activity_name}/signup adds a participant"""
    # Arrange
    test_email = "testuser_signup@mergington.edu"
    activity_name = "Chess Club"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    
    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert test_email in result["message"]
    assert activity_name in result["message"]
    
    # Verify participant was added
    check_response = client.get("/activities")
    updated_participants = check_response.json()[activity_name]["participants"]
    assert test_email in updated_participants


def test_signup_duplicate_fails():
    """Test that signing up the same email twice returns HTTP 400"""
    # Arrange
    test_email = "duplicate_test@mergington.edu"
    activity_name = "Programming Class"
    
    # Act - first signup (should succeed)
    response1 = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    
    # Assert first signup succeeded
    assert response1.status_code == 200
    
    # Act - attempt duplicate signup (should fail)
    response2 = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    
    # Assert second signup failed with 400
    assert response2.status_code == 400
    result = response2.json()
    assert "already signed up" in result["detail"]


def test_signup_nonexistent_activity_returns_404():
    """Test that signing up for a non-existent activity returns HTTP 404"""
    # Arrange
    test_email = "testuser@mergington.edu"
    nonexistent_activity = "Nonexistent Club"
    
    # Act
    response = client.post(f"/activities/{nonexistent_activity}/signup?email={test_email}")
    
    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "not found" in result["detail"].lower()


def test_remove_participant():
    """Test that DELETE /activities/{activity_name}/participants removes a participant"""
    # Arrange
    test_email = "remove_test@mergington.edu"
    activity_name = "Gym Class"
    
    # First, sign up the participant
    client.post(f"/activities/{activity_name}/signup?email={test_email}")
    
    # Act - remove the participant
    response = client.delete(f"/activities/{activity_name}/participants?email={test_email}")
    
    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert test_email in result["message"]
    
    # Verify participant was removed
    check_response = client.get("/activities")
    updated_participants = check_response.json()[activity_name]["participants"]
    assert test_email not in updated_participants


def test_remove_missing_participant_returns_404():
    """Test that removing a non-existent participant returns HTTP 404"""
    # Arrange
    test_email = "nonexistent_remove@mergington.edu"
    activity_name = "Basketball Team"
    
    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={test_email}")
    
    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "not found" in result["detail"].lower()


def test_remove_from_nonexistent_activity_returns_404():
    """Test that removing from a non-existent activity returns HTTP 404"""
    # Arrange
    test_email = "testuser@mergington.edu"
    nonexistent_activity = "Nonexistent Club"
    
    # Act
    response = client.delete(f"/activities/{nonexistent_activity}/participants?email={test_email}")
    
    # Assert
    assert response.status_code == 404


def test_root_redirects_to_static():
    """Test that GET / redirects to /static/index.html"""
    # Arrange - expect redirect to static content
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307
    assert "/static/index.html" in response.headers["location"]
