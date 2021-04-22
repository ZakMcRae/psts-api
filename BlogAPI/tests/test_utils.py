import pytest
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from BlogAPI.db.SQLAlchemy_models import User
from BlogAPI.tests.test_db_setup import TestingSessionLocal
from BlogAPI.util.utils import validate_new_user, authenticate_user


def test_authenticate_user():
    db: Session = TestingSessionLocal()

    # successful test case user info
    username = "zaktest"
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
    username = "zaktest"
    password = "password"
    authenticated_user = authenticate_user(db, username, password)
    assert authenticated_user is False


def test_validate_new_user():
    db = TestingSessionLocal()

    # fail case invalid username
    with pytest.raises(HTTPException):
        validate_new_user(db, "zaktest", "jim@example.com")

    # fail case invalid email
    with pytest.raises(HTTPException):
        validate_new_user(db, "jim", "zaktest@example.com")

    # test valid email and username
    assert validate_new_user(db, "jim", "jim@example.com") is True
