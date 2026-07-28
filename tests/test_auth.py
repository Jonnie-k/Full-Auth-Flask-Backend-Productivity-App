def test_signup_success(client, db):
    resp = client.post("/auth/signup", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "securepass",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert "access_token" in data
    assert data["user"]["username"] == "newuser"


def test_signup_duplicate_username(client, test_user):
    resp = client.post("/auth/signup", json={
        "username": "tester",
        "email": "other@example.com",
        "password": "securepass",
    })
    assert resp.status_code == 422


def test_signup_missing_fields(client, db):
    resp = client.post("/auth/signup", json={"username": "incomplete"})
    assert resp.status_code == 422


def test_login_success(client, test_user):
    resp = client.post("/auth/login", json={"username": "tester", "password": "password123"})
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()


def test_login_wrong_password(client, test_user):
    resp = client.post("/auth/login", json={"username": "tester", "password": "wrongpass"})
    assert resp.status_code == 401


def test_login_nonexistent_user(client, db):
    resp = client.post("/auth/login", json={"username": "ghost", "password": "pass"})
    assert resp.status_code == 401


def test_me_authenticated(client, auth_headers):
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["username"] == "tester"


def test_me_unauthenticated(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_logout(client, auth_headers):
    resp = client.delete("/auth/logout", headers=auth_headers)
    assert resp.status_code == 200

    # Token should be revoked now
    resp2 = client.get("/auth/me", headers=auth_headers)
    assert resp2.status_code == 401


def test_signup_short_password(client, db):
    resp = client.post("/auth/signup", json={
        "username": "shortpass",
        "email": "short@example.com",
        "password": "abc",
    })
    assert resp.status_code == 422
