import pytest


def test_create_dataset(client, auth_headers):
    response = client.post("/api/v1/datasets/", json={
        "title": "Test Dataset",
        "slug": "test-dataset",
        "description": "A test dataset",
        "is_public": True
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "dataset" in data
    assert data["dataset"]["title"] == "Test Dataset"
    assert "upload_url" in data


def test_list_datasets_empty(client):
    response = client.get("/api/v1/datasets/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_dataset_by_id(client, auth_headers):
    create_resp = client.post("/api/v1/datasets/", json={
        "title": "Test Dataset",
        "slug": "test-dataset-2",
        "description": "A test dataset",
        "is_public": True
    }, headers=auth_headers)
    dataset_id = create_resp.json()["dataset"]["id"]

    response = client.get(f"/api/v1/datasets/{dataset_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Dataset"


def test_update_dataset_unauthorized(client, auth_headers):
    # Create a dataset as testuser
    create_resp = client.post("/api/v1/datasets/", json={
        "title": "Test Dataset",
        "slug": "test-dataset-3",
        "description": "A test dataset",
        "is_public": True
    }, headers=auth_headers)
    dataset_id = create_resp.json()["dataset"]["id"]

    # Create another user
    client.post("/api/v1/auth/register", json={
        "username": "otheruser",
        "email": "other@example.com",
        "password": "otherpass123"
    })
    login_resp = client.post("/api/v1/auth/login", data={
        "username": "otheruser",
        "password": "otherpass123"
    })
    other_token = login_resp.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    # Try to update dataset as other user
    response = client.put(f"/api/v1/datasets/{dataset_id}", json={
        "title": "Hacked Dataset"
    }, headers=other_headers)
    assert response.status_code == 403


def test_delete_dataset_owner(client, auth_headers):
    create_resp = client.post("/api/v1/datasets/", json={
        "title": "To Delete",
        "slug": "to-delete",
        "description": "Will be deleted",
        "is_public": True
    }, headers=auth_headers)
    dataset_id = create_resp.json()["dataset"]["id"]

    response = client.delete(f"/api/v1/datasets/{dataset_id}", headers=auth_headers)
    assert response.status_code == 200

    # Verify deletion
    get_resp = client.get(f"/api/v1/datasets/{dataset_id}")
    assert get_resp.status_code == 404
