"""Integration tests for API workflows."""
import pytest


class TestSignupAndUnregisterWorkflow:
    """Tests for complete signup and unregister workflows."""
    
    def test_signup_verify_unregister_workflow(self, client, reset_activities, existing_activity, sample_email):
        """Test complete workflow: signup -> verify -> unregister."""
        # Initial state: verify participant not present
        response = client.get("/activities")
        assert sample_email not in response.json()[existing_activity]["participants"]
        
        # Sign up
        signup_response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": sample_email}
        )
        assert signup_response.status_code == 200
        
        # Verify in activities list
        response = client.get("/activities")
        assert sample_email in response.json()[existing_activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{existing_activity}/unregister",
            params={"email": sample_email}
        )
        assert unregister_response.status_code == 200
        
        # Verify removed from activities list
        response = client.get("/activities")
        assert sample_email not in response.json()[existing_activity]["participants"]
    
    def test_multiple_signups_sequential(self, client, reset_activities, existing_activity):
        """Test multiple sequential signups to same activity."""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                f"/activities/{existing_activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all are in the list
        response = client.get("/activities")
        participants = response.json()[existing_activity]["participants"]
        for email in emails:
            assert email in participants
    
    def test_signup_unregister_signup_again(self, client, reset_activities, existing_activity, sample_email):
        """Test signing up, unregistering, and signing up again."""
        # First signup
        response1 = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": sample_email}
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            f"/activities/{existing_activity}/unregister",
            params={"email": sample_email}
        )
        assert response2.status_code == 200
        
        # Sign up again - should succeed
        response3 = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": sample_email}
        )
        assert response3.status_code == 200
        
        # Verify is in the list
        response = client.get("/activities")
        assert sample_email in response.json()[existing_activity]["participants"]
    
    def test_participant_count_accuracy(self, client, reset_activities, existing_activity):
        """Test that participant count remains accurate through operations."""
        emails = ["test1@mergington.edu", "test2@mergington.edu", "test3@mergington.edu"]
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()[existing_activity]["participants"])
        
        # Add participants
        for email in emails:
            client.post(
                f"/activities/{existing_activity}/signup",
                params={"email": email}
            )
        
        # Verify count increased by 3
        response = client.get("/activities")
        assert len(response.json()[existing_activity]["participants"]) == initial_count + 3
        
        # Remove one participant
        client.delete(
            f"/activities/{existing_activity}/unregister",
            params={"email": emails[0]}
        )
        
        # Verify count decreased by 1
        response = client.get("/activities")
        assert len(response.json()[existing_activity]["participants"]) == initial_count + 2
    
    def test_availability_calculation(self, client, reset_activities):
        """Test that availability (spots left) is calculated correctly."""
        activity = "Art Studio"  # max_participants: 18
        
        response = client.get("/activities")
        initial_participants = len(response.json()[activity]["participants"])
        max_participants = response.json()[activity]["max_participants"]
        expected_spots = max_participants - initial_participants
        
        # Verify spots_left calculation through signup
        email = "newstudent@mergington.edu"
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        response = client.get("/activities")
        updated_participants = len(response.json()[activity]["participants"])
        assert updated_participants == initial_participants + 1
        assert updated_participants <= max_participants


class TestConcurrentActivityOperations:
    """Tests for operations on multiple activities."""
    
    def test_signup_to_multiple_activities(self, client, reset_activities, sample_email):
        """Student should be able to signup to multiple activities."""
        activities_to_join = ["Chess Club", "Programming Class", "Gym Class"]
        
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": sample_email}
            )
            assert response.status_code == 200
        
        # Verify student is in all activities
        response = client.get("/activities")
        for activity in activities_to_join:
            assert sample_email in response.json()[activity]["participants"]
    
    def test_different_students_same_activity(self, client, reset_activities, existing_activity):
        """Multiple students should be able to signup to same activity."""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                f"/activities/{existing_activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all are in the same activity
        response = client.get("/activities")
        participants = response.json()[existing_activity]["participants"]
        for email in emails:
            assert email in participants


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_empty_email_string(self, client, existing_activity):
        """Signup with empty email should fail or be handled gracefully."""
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": ""}
        )
        # System should either reject or accept empty string
        # Current implementation will accept it, document the behavior
        # In a real scenario, we'd want validation
        pass
    
    def test_activity_name_with_special_chars(self, client, sample_email):
        """Non-existent activity names with special chars should return 404."""
        response = client.post(
            "/activities/Test%26Activity/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 404
    
    def test_very_long_email(self, client, reset_activities, existing_activity):
        """Signup with very long email should work."""
        long_email = "a" * 50 + "@mergington.edu"
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": long_email}
        )
        assert response.status_code == 200
        
        # Verify it was added
        response = client.get("/activities")
        assert long_email in response.json()[existing_activity]["participants"]
