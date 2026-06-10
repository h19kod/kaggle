import pytest


def test_create_notebook(client, auth_headers):
    response = client.post("/api/v1/notebooks/", json={
        "title": "Test Notebook",
        "language": "python",
        "code": "print('hello')",
        "is_public": True
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Notebook"
    assert data["language"] == "python"


def test_fork_notebook(client, auth_headers):
    # Create original notebook
    create_resp = client.post("/api/v1/notebooks/", json={
        "title": "Original Notebook",
        "language": "python",
        "code": "print('original')",
        "is_public": True
    }, headers=auth_headers)
    notebook_id = create_resp.json()["id"]

    # Fork it
    response = client.post(f"/api/v1/notebooks/{notebook_id}/fork", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Fork of Original Notebook"
    assert data["forked_from_id"] == notebook_id


def test_list_notebooks(client):
    response = client.get("/api/v1/notebooks/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_notebook_owner_only(client, auth_headers):
    create_resp = client.post("/api/v1/notebooks/", json={
        "title": "My Notebook",
        "language": "python",
        "code": "print('mine')",
        "is_public": True
    }, headers=auth_headers)
    notebook_id = create_resp.json()["id"]

    # Update as owner
    response = client.put(f"/api/v1/notebooks/{notebook_id}", json={
        "title": "Updated Notebook"
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Notebook"
