import pytest
from datetime import datetime, timezone, timedelta


def test_create_competition(client, auth_headers):
    response = client.post("/api/v1/competitions/", json={
        "title": "Test Competition",
        "description_markdown": "A test competition",
        "evaluation_metric": "accuracy",
        "start_date": datetime.now(timezone.utc).isoformat(),
        "end_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Competition"
    assert data["evaluation_metric"] == "accuracy"


def test_list_competitions(client):
    response = client.get("/api/v1/competitions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_deadline_enforcement(client, auth_headers):
    # Create an expired competition
    create_resp = client.post("/api/v1/competitions/", json={
        "title": "Expired Competition",
        "description_markdown": "Expired",
        "evaluation_metric": "accuracy",
        "start_date": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
        "end_date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    }, headers=auth_headers)
    assert create_resp.status_code == 200
    competition_id = create_resp.json()["id"]

    # Try to submit after deadline
    response = client.post(f"/api/v1/competitions/{competition_id}/submissions", json={
        "submitted_file_url": "http://example.com/submission.csv"
    }, headers=auth_headers)
    assert response.status_code == 400


def test_leaderboard_cache(client, auth_headers):
    pytest.skip("Requires Redis connection")
    # Create active competition
    create_resp = client.post("/api/v1/competitions/", json={
        "title": "Active Competition",
        "description_markdown": "Active",
        "evaluation_metric": "accuracy",
        "start_date": datetime.now(timezone.utc).isoformat(),
        "end_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    }, headers=auth_headers)
    competition_id = create_resp.json()["id"]

    # Get leaderboard
    response = client.get(f"/api/v1/competitions/{competition_id}/leaderboard")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
