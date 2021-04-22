import json

import jwt

from BlogAPI.tests.test_db_setup import client, db_non_commit


def test_generate_token():
    # successful test case - valid username and email
    body = {
        "username": "zaktest",
        "password": 123,
    }
    header = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    resp = client.post("/token", body, headers=header)
    token_info = resp.json()

    assert resp.status_code == 200
    assert token_info.get("access_token") is not None
    assert token_info.get("token_type") == "bearer"

    # wrong username case
    body = {
        "username": "jim",
        "password": 123,
    }
    header = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    resp = client.post("/token", body, headers=header)

    assert resp.status_code == 401
    assert resp.json() == {"detail": "Invalid Username or Password"}

    # wrong password case
    body = {
        "username": "zaktest",
        "password": "password",
    }
    header = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    resp = client.post("/token", body, headers=header)

    assert resp.status_code == 401
    assert resp.json() == {"detail": "Invalid Username or Password"}


def test_get_user():
    # successful test case
    resp = client.get("/user/<user-id>?user_id=1")

    assert resp.status_code == 200
    assert resp.json() == {
        "username": "zaktest",
        "email": "zaktest@example.com",
        "id": 1,
    }


def test_create_user(db_non_commit):
    # db_non_commit - allows testing without database changes

    # successful test case
    body = {"username": "zoetest", "email": "zoetest@example.com", "password": 123}
    resp = client.post("/user", json.dumps(body))
    user_info = resp.json()

    assert resp.status_code == 200
    assert user_info.get("username") == "zoetest"
    assert user_info.get("email") == "zoetest@example.com"

    # taken username case
    body = {"username": "zaktest", "email": "zoetest@example.com", "password": 123}
    resp = client.post("/user", json.dumps(body))

    assert resp.status_code == 409
    assert resp.json() == {"detail": "Username is taken, please try another"}

    # taken email case
    body = {"username": "zoetest", "email": "zaktest@example.com", "password": 123}
    resp = client.post("/user", json.dumps(body))

    assert resp.status_code == 409
    assert resp.json() == {"detail": "Email is taken, please try another"}


def test_get_me(monkeypatch):
    # fail case - invalid token
    header = {"Authorization": "Bearer a.fake.token"}
    resp = client.get("/user/me", headers=header)

    assert resp.status_code == 401
    assert resp.json() == {"detail": "Invalid token"}

    # fail case - expired token
    # token stored outside of git in test_info.json
    with open(
        r"C:\Users\Zak\PycharmProjects\BlogAPI\BlogAPI\tests\test_info.json"
    ) as fin:
        test_info = json.load(fin)

    header = {"Authorization": f"Bearer {test_info.get('expired_test_token')}"}
    resp = client.get("/user/me", headers=header)

    assert resp.status_code == 401
    assert resp.json() == {"detail": "Token is expired"}

    # successful test case
    def mock_return_valid(*args, **kwargs):
        user_info = {"id": 1, "username": "zaktest", "exp": 1621605216}
        return user_info

    # simulates jwt.decode being called - returns mock output "user_info"
    monkeypatch.setattr(jwt, "decode", mock_return_valid)

    header = {"Authorization": "Bearer a.fake.token"}
    resp = client.get("/user/me", headers=header)

    assert resp.status_code == 200
    assert resp.json() == {
        "username": "zaktest",
        "email": "zaktest@example.com",
        "id": 1,
    }
