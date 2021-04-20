import pytest
from fastapi.exceptions import HTTPException

from BlogAPI.tests.test_db_setup import client, TestingSessionLocal
from BlogAPI.util.utils import validate_new_user


def test_get_user():
    resp = client.get("/get_user_test?user_id=1")

    assert resp.status_code == 200
    # todo - update to actually hashed hs_password
    assert resp.json() == {
        "id": 1,
        "email": "zak@example.com",
        "username": "zak",
        "hs_password": "password",
    }


def test_validate_new_user():
    db = TestingSessionLocal()

    # test only valid email
    with pytest.raises(HTTPException):
        validate_new_user(db, "zak", "jim@example.com")

    # test only valid username
    with pytest.raises(HTTPException):
        validate_new_user(db, "jim", "zak@example.com")

    # test valid email and username
    assert validate_new_user(db, "jim", "jim@example.com") is True
