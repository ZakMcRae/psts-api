from BlogAPI.tests.test_db_setup import client
from sqlalchemy.orm import Session
import json


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


def test_get_user():
    # successful test case
    resp = client.get("/user/<user-id>?user_id=1")

    # successful test case
    assert resp.status_code == 200
    assert resp.json() == {
        "username": "zaktest",
        "email": "zaktest@example.com",
        "id": 1,
    }


def test_create_user(monkeypatch):
    # successful test case
    def mock_return(*args, **kwargs):
        pass

    monkeypatch.setattr(Session, "add", mock_return)
    monkeypatch.setattr(Session, "commit", mock_return)
    monkeypatch.setattr(Session, "refresh", mock_return)

    body = {"username": "zoetest", "email": "zoetest@example.com", "password": 123}
    resp = client.post("/user", json.dumps(body))

    assert resp.status_code == 200

    # todo other test cases
