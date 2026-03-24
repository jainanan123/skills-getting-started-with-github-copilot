"""Unit tests for FastAPI endpoints."""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_200(self, client):
        """GET /activities should return 200 status code."""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """GET /activities should return a dictionary."""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_has_expected_count(self, client):
        """GET /activities should return all activities."""
        response = client.get("/activities")
        activities = response.json()
        # App initializes with 9 activities
        assert len(activities) == 9
    
    def test_get_activities_structure(self, client):
        """GET /activities should return activities with correct structure."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_participant_emails(self, client):
        """GET /activities should return valid participant emails."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_data in activities.values():
            for participant in activity_data["participants"]:
                # Skip empty strings (edge case test data)
                if participant:
                    assert isinstance(participant, str)
                    assert "@" in participant


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client, reset_activities, existing_activity, sample_email):
        """Signup to existing activity with new email should return 200."""
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
    
    def test_signup_adds_participant(self, client, reset_activities, existing_activity, sample_email):
        """Signup should add participant to activity."""
        # Get initial count
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[existing_activity]["participants"])
        
        # Sign up
        client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": sample_email}
        )
        
        # Get updated count
        response_after = client.get("/activities")
        updated_count = len(response_after.json()[existing_activity]["participants"])
        
        assert updated_count == initial_count + 1
        assert sample_email in response_after.json()[existing_activity]["participants"]
    
    def test_signup_duplicate_returns_400(self, client, reset_activities, existing_activity, existing_participant):
        """Signup with existing participant should return 400."""
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": existing_participant}
        )
        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()
    
    def test_signup_nonexistent_activity_returns_404(self, client, sample_email):
        """Signup to non-existent activity should return 404."""
        response = client.post(
            "/activities/NonexistentActivity/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_missing_email_parameter(self, client, existing_activity):
        """Signup without email parameter should fail."""
        response = client.post(f"/activities/{existing_activity}/signup")
        # FastAPI will return 422 for missing required parameter
        assert response.status_code == 422
    
    def test_signup_special_characters_in_email(self, client, reset_activities, existing_activity):
        """Signup with special characters in email should work."""
        special_email = "test+tag@mergington.edu"
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": special_email}
        )
        assert response.status_code == 200


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success(self, client, reset_activities, existing_activity, existing_participant):
        """Unregister existing participant should return 200."""
        response = client.delete(
            f"/activities/{existing_activity}/unregister",
            params={"email": existing_participant}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities, existing_activity, existing_participant):
        """Unregister should remove participant from activity."""
        # Get initial count
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[existing_activity]["participants"])
        
        # Unregister
        client.delete(
            f"/activities/{existing_activity}/unregister",
            params={"email": existing_participant}
        )
        
        # Get updated count
        response_after = client.get("/activities")
        updated_count = len(response_after.json()[existing_activity]["participants"])
        
        assert updated_count == initial_count - 1
        assert existing_participant not in response_after.json()[existing_activity]["participants"]
    
    def test_unregister_nonexistent_participant_returns_400(self, client, reset_activities, existing_activity, sample_email):
        """Unregister non-registered participant should return 400."""
        response = client.delete(
            f"/activities/{existing_activity}/unregister",
            params={"email": sample_email}
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()
    
    def test_unregister_nonexistent_activity_returns_404(self, client, existing_participant):
        """Unregister from non-existent activity should return 404."""
        response = client.delete(
            "/activities/NonexistentActivity/unregister",
            params={"email": existing_participant}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_missing_email_parameter(self, client, existing_activity):
        """Unregister without email parameter should fail."""
        response = client.delete(f"/activities/{existing_activity}/unregister")
        assert response.status_code == 422
    
    def test_unregister_twice_returns_400(self, client, reset_activities, existing_activity, existing_participant):
        """Unregister same participant twice should fail on second attempt."""
        # First unregister succeeds
        response1 = client.delete(
            f"/activities/{existing_activity}/unregister",
            params={"email": existing_participant}
        )
        assert response1.status_code == 200
        
        # Second unregister fails
        response2 = client.delete(
            f"/activities/{existing_activity}/unregister",
            params={"email": existing_participant}
        )
        assert response2.status_code == 400


class TestActivityNaming:
    """Tests for activity name handling (encoding, case sensitivity, etc)."""
    
    def test_signup_with_url_encoded_activity_name(self, client, reset_activities, sample_email):
        """Signup with URL-encoded activity name should work."""
        # "Chess Club" needs to be encoded as "Chess%20Club"
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200
    
    def test_signup_activity_name_case_sensitive(self, client, sample_email):
        """Activity name lookup should be case sensitive."""
        response = client.post(
            "/activities/chess club/signup",
            params={"email": sample_email}
        )
        # Should fail because "chess club" != "Chess Club"
        assert response.status_code == 404
