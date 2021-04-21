import jwt
import pytest
from fastapi.exceptions import HTTPException
from jwt import DecodeError
from sqlalchemy.orm import Session

from BlogAPI.db.SQLAlchemy_models import User
from BlogAPI.tests.test_db_setup import TestingSessionLocal
from BlogAPI.util.utils import validate_new_user, authenticate_user, get_current_user


def test_authenticate_user():
    db: Session = TestingSessionLocal()

    # successful test case user info
    username = "zak"
    password = "123"
    authenticated_user = authenticate_user(db, username, password)

    # actual user info from test.db
    user_in_db = db.query(User).filter_by(username=username).first()

    # successful test
    assert authenticated_user == user_in_db

    # wrong username case
    username = "jim"
    password = "123"
    authenticated_user = authenticate_user(db, username, password)
    assert authenticated_user is False

    # wrong password case
    username = "zak"
    password = "password"
    authenticated_user = authenticate_user(db, username, password)
    assert authenticated_user is False


def test_get_current_user(monkeypatch):
    db = TestingSessionLocal()

    # fail test case for an invalid or expired token
    with pytest.raises(HTTPException):
        get_current_user(db, "a.fake.token")

    # successful test case
    # monkeypatch jwt.decode() to return mock user_info - to avoid using a real token
    def mock_return(*args, **kwargs):
        user_info = {"id": 1, "username": "zak", "exp": 1621605216}
        return user_info

    monkeypatch.setattr(jwt, "decode", mock_return)

    user = get_current_user(db, "fake token")
    assert user.username == "zak"
    assert user.email == "zak@example.com"


def test_validate_new_user():
    db = TestingSessionLocal()

    # fail case invalid username
    with pytest.raises(HTTPException):
        validate_new_user(db, "zak", "jim@example.com")

    # fail case invalid email
    with pytest.raises(HTTPException):
        validate_new_user(db, "jim", "zak@example.com")

    # test valid email and username
    assert validate_new_user(db, "jim", "jim@example.com") is True
