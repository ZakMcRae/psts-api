import pytest
from fastapi.exceptions import HTTPException
from sqlalchemy import select, func

from BlogAPI.db.SQLAlchemy_models import User
from BlogAPI.db.db_session_async import create_async_session
from BlogAPI.tests.test_setup_and_utils import TestingSessionLocal
from BlogAPI.util.utils import validate_new_user, authenticate_user


@pytest.mark.asyncio
async def test_authenticate_user():
    # successful test case user info
    username = "zaktest"
    password = "123"
    authenticated_user = await authenticate_user(username, password)

    # actual user info from test.db
    async with create_async_session() as session:
        query = select(User).filter(func.lower(User.username) == username.lower())
        result = await session.execute(query)
        user_in_db = result.scalar_one_or_none()

    # successful test
    assert authenticated_user == user_in_db

    # wrong username case
    username = "jim"
    password = "123"
    authenticated_user = await authenticate_user(username, password)
    assert authenticated_user is False

    # wrong password case
    username = "zaktest"
    password = "password"
    authenticated_user = await authenticate_user(username, password)
    assert authenticated_user is False


@pytest.mark.asyncio
async def test_validate_new_user():
    db = TestingSessionLocal()

    # fail case taken username
    with pytest.raises(HTTPException):
        await validate_new_user("zaktest", "jim@example.com")

    # fail case taken email
    with pytest.raises(HTTPException):
        await validate_new_user("jim", "zaktest@example.com")

    # test valid email and username (both not taken)
    assert await validate_new_user("jim", "jim@example.com") is True
