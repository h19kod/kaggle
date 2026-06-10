import pytest


def test_register_user(client):
    response = client.post("/api/v1/auth/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "newpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert "id" in data
    assert "password_hash" not in data


def test_register_duplicate_username(client, test_user):
    response = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "another@example.com",
        "password": "newpass123"
    })
    assert response.status_code == 400


def test_login_success(client, test_user):
    response = client.post("/api/v1/auth/login", data={
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post("/api/v1/auth/login", data={
        "username": "wronguser",
        "password": "wrongpass"
    })
    assert response.status_code == 400


def test_get_current_user(client, auth_headers):
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data


def test_get_current_user_no_token(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
