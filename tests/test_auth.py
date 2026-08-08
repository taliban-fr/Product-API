def test_register_user(client):
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_username(client):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
    }
    client.post("/register", json=user_data)

    duplicate = user_data.copy()
    duplicate["email"] = "different@example.com"
    response = client.post("/register", json=duplicate)
    assert response.status_code == 409


def test_login_success(client):
    client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        },
    )

    response = client.post(
        "/login", data={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        },
    )

    response = client.post(
        "/login", data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
