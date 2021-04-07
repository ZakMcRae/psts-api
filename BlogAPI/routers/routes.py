import datetime

import jwt
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from BlogAPI.config import config_settings
from BlogAPI.db import db_session
from BlogAPI.db.SQLAlchemy_models import User
from BlogAPI.util.mock_data import (
    add_sample_users,
    add_sample_posts,
    add_sample_replies,
    add_sample_follows,
)
from BlogAPI.util.utils import get_current_user, authenticate_user

router = APIRouter()


@router.get("/me")
def get_user(user=Depends(get_current_user)):
    return {"username": user.username, "email": user.email, "id": user.id}


@router.post("/token")
def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Username or Password",
        )

    user_info = {
        "id": user.id,
        "username": user.username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30),
    }

    token = jwt.encode(user_info, config_settings.secret_key)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/test")
def test():
    # username = "elliot"
    # session = db_session.create_session()
    # user = session.query(User).filter_by(username=username).first()
    return authenticate_user("theo", "123")


@router.get("/query_users")
def query_users():
    session = db_session.create_session()
    x = session.query(User).all()
    # y = session.query(User).filter_by(id=1).first()
    # z = session.query(User).filter_by(name="Jess").first()
    return x


@router.get("/add_users")
def add_users():
    return add_sample_users()


@router.get("/add_posts")
def add_posts():
    return add_sample_posts()


@router.get("/add_replies")
def add_replies():
    return add_sample_replies()


@router.get("/add_follows")
def add_follows():
    return add_sample_follows()
