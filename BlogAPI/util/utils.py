from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette import status

from BlogAPI.db.SQLAlchemy_models import User


def authenticate_user(db: Session, username: str, password: str) -> User:
    """
    Make sure username is in database and password matches hashed password in database
    """
    user = db.query(User).filter(func.lower(User.username) == username.lower()).first()
    if not user:
        return False

    if not user.verify_password(password):
        return False

    return user


def validate_new_user(db: Session, username: str, email: str) -> bool:
    """
    Makes sure username and email are not already taken in database
    """

    db_username = (
        db.query(User.username)
        .filter(func.lower(User.username) == username.lower())
        .scalar()
    )
    if db_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is taken, please try another",
        )

    db_email = (
        db.query(User.email).filter(func.lower(User.email) == email.lower()).scalar()
    )
    if db_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is taken, please try another",
        )

    return True
