import jwt
from fastapi import Depends, HTTPException
from starlette import status

from BlogAPI.config import config_settings
from BlogAPI.db import db_session
from BlogAPI.db.SQLAlchemy_models import User
from BlogAPI.dependencies.dependencies import oauth2_scheme


def authenticate_user(username: str, password: str) -> User:
    session = db_session.create_session()
    user = session.query(User).filter_by(username=username).first()

    if not user:
        return False

    if not user.verify_password(password):
        return False

    return user


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        user_info = jwt.decode(token, config_settings.secret_key, algorithms=["HS256"])
        session = db_session.create_session()
        user = session.query(User).get(user_info.get("id"))
        return user

    except HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Username or Password",
        )
