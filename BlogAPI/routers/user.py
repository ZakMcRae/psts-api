import datetime
from typing import List

import jwt
from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from starlette import status

from BlogAPI.config import config_settings
from BlogAPI.db import db_session
from BlogAPI.db.SQLAlchemy_models import User, Post, Reply
from BlogAPI.pydantic_models.pydantic_models import UserIn, UserOut, PostOut
from BlogAPI.util.utils import get_current_user, validate_new_user, authenticate_user

router = APIRouter()


@router.post("/user", response_model=UserOut)
def create_user(user_in: UserIn):
    if validate_new_user(user_in.username, user_in.email):
        hs_password = bcrypt.hash(user_in.password)
        user = User(
            username=user_in.username,
            email=user_in.email,
            hs_password=hs_password,
        )

        session = db_session.create_session()
        session.add(user)
        session.commit()
        print(user)
        return user

    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


@router.get("/user/me", response_model=UserOut)
def get_me(user=Depends(get_current_user)):
    return user


@router.get("/user/<user_id>", response_model=UserOut)
def get_user(user_id: int):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    return user


@router.get("/user/<user_id>/posts", response_model=List[PostOut])
def get_users_posts(
    user_id: int, skip: int = 0, limit: int = 10, sort_newest_first: bool = True
):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    user_posts: List[Post] = user.posts

    if not sort_newest_first:
        user_posts.sort(key=lambda post: post.date_created)

    return user_posts[skip : skip + limit]


@router.get("/user/<user_id>/replies")
def get_users_replies(
    user_id: int, skip: int = 0, limit: int = 10, sort_newest_first: bool = True
):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    user_replies: List[Reply] = user.replies

    if not sort_newest_first:
        user_replies.sort(key=lambda reply: reply.date_created)

    return user_replies[skip : skip + limit]
