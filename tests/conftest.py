"""Shared fixtures and configuration for tests."""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    from app import activities
    
    # Store original state
    original_state = {
        key: {
            "description": value["description"],
            "schedule": value["schedule"],
            "max_participants": value["max_participants"],
            "participants": value["participants"].copy()
        }
        for key, value in activities.items()
    }
    
    yield
    
    # Restore original state after test
    activities.clear()
    for key, value in original_state.items():
        activities[key] = {
            "description": value["description"],
            "schedule": value["schedule"],
            "max_participants": value["max_participants"],
            "participants": value["participants"].copy()
        }


@pytest.fixture
def sample_email():
    """Provide a sample email for testing."""
    return "test.student@mergington.edu"


@pytest.fixture
def existing_activity():
    """Provide an existing activity name for testing."""
    return "Chess Club"


@pytest.fixture
def existing_participant():
    """Provide an existing participant email from Chess Club."""
    return "michael@mergington.edu"


@pytest.fixture
def full_activity():
    """Create a full activity for testing capacity limits."""
    from app import activities
    # Use Drama Club and add more participants
    activity = activities["Drama Club"]
    original_count = len(activity["participants"])
    # Fill it to capacity (max is 25)
    for i in range(activity["max_participants"] - original_count):
        activity["participants"].append(f"filler{i}@mergington.edu")
    yield "Drama Club"
    # Cleanup is handled by reset_activities fixture
