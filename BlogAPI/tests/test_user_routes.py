import json

import pytest
from sqlalchemy.orm import Session

from BlogAPI.tests.test_db_setup import client, db_non_commit
from fastapi.exceptions import HTTPException


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
