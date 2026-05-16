import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = copy.deepcopy(original_activities)


def test_get_activities_returns_activity_data():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = quote("Chess Club", safe="")
    email = "teststudent@mergington.edu"
    url = f"/activities/{activity_name}/signup?email={quote(email, safe='')}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    details = client.get("/activities").json()["Chess Club"]
    assert email in details["participants"]


def test_duplicate_signup_returns_bad_request():
    # Arrange
    activity_name = quote("Chess Club", safe="")
    email = "michael@mergington.edu"
    url = f"/activities/{activity_name}/signup?email={quote(email, safe='')}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_unsubscribes_student():
    # Arrange
    activity_name = quote("Chess Club", safe="")
    email = "michael@mergington.edu"
    url = f"/activities/{activity_name}/participants?email={quote(email, safe='')}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"

    details = client.get("/activities").json()["Chess Club"]
    assert email not in details["participants"]


def test_remove_missing_participant_returns_not_found():
    # Arrange
    activity_name = quote("Chess Club", safe="")
    email = "missingstudent@mergington.edu"
    url = f"/activities/{activity_name}/participants?email={quote(email, safe='')}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
