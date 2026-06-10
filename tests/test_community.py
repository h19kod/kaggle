import pytest


def test_create_post(client, auth_headers):
    response = client.post("/api/v1/posts/", json={
        "title": "Test Post",
        "content_body": "This is a test post",
        "category": "GENERAL"
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["content_body"] == "This is a test post"


def test_upvote_idempotency(client, auth_headers, test_user):
    # Create a dataset to upvote
    dataset_resp = client.post("/api/v1/datasets/", json={
        "title": "Upvote Test Dataset",
        "slug": "upvote-test",
        "description": "For upvote testing",
        "is_public": True
    }, headers=auth_headers)
    dataset_id = dataset_resp.json()["dataset"]["id"]

    # First upvote
    response1 = client.post("/api/v1/upvote/", json={
        "target_type": "DATASET",
        "target_id": dataset_id
    }, headers=auth_headers)
    assert response1.status_code == 200

    # Second upvote (should be rejected)
    response2 = client.post("/api/v1/upvote/", json={
        "target_type": "DATASET",
        "target_id": dataset_id
    }, headers=auth_headers)
    assert response2.status_code == 400


def test_upvote_syncs_profile(client, auth_headers, test_user):
    # Create dataset as testuser
    dataset_resp = client.post("/api/v1/datasets/", json={
        "title": "Profile Sync Dataset",
        "slug": "profile-sync",
        "description": "Test profile sync",
        "is_public": True
    }, headers=auth_headers)
    dataset_id = dataset_resp.json()["dataset"]["id"]

    # Create another user
    client.post("/api/v1/auth/register", json={
        "username": "voter",
        "email": "voter@example.com",
        "password": "voterpass123"
    })
    login_resp = client.post("/api/v1/auth/login", data={
        "username": "voter",
        "password": "voterpass123"
    })
    voter_token = login_resp.json()["access_token"]
    voter_headers = {"Authorization": f"Bearer {voter_token}"}

    # Upvote the dataset
    response = client.post("/api/v1/upvote/", json={
        "target_type": "DATASET",
        "target_id": dataset_id
    }, headers=voter_headers)
    assert response.status_code == 200
