import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError
from sqlalchemy.orm import Session
from starlette import status

from BlogAPI.config import config_settings
from BlogAPI.db.SQLAlchemy_models import User
from BlogAPI.db.db_session import SessionLocal


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Returns User object based on user_id stored in token(JWT)
    """
    try:
        user_info = jwt.decode(token, config_settings.secret_key, algorithms=["HS256"])
        return db.query(User).get(user_info.get("id"))

    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Username or Password",
        )

    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is expired",
        )
