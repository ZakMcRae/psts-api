from fastapi import HTTPException
from sqlalchemy import func, select
from starlette import status

from BlogAPI.db.SQLAlchemy_models import User
from BlogAPI.db.db_session_async import create_async_session


async def authenticate_user(username: str, password: str) -> User:
    """
    Make sure username is in database and password matches hashed password in database
    """
    async with create_async_session() as session:
        query = select(User).filter(func.lower(User.username) == username.lower())
        result = await session.execute(query)
        user = result.scalar_one_or_none()

    if not user:
        return False

    if not user.verify_password(password):
        return False

    return user


async def validate_new_user(username: str, email: str) -> bool:
    """
    Makes sure username and email are not already taken in database
    """
    async with create_async_session() as session:
        query = select(User.username).filter(
            func.lower(User.username) == username.lower()
        )
        result = await session.execute(query)
        db_username = result.scalar_one_or_none()

    if db_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is taken, please try another",
        )

    async with create_async_session() as session:
        query = select(User.email).filter(func.lower(User.email) == email.lower())
        result = await session.execute(query)
        db_email = result.scalar_one_or_none()

    if db_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is taken, please try another",
        )

    return True
