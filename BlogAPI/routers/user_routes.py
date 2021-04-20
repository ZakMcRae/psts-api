import datetime
from typing import List

import jwt
from fastapi import Depends, APIRouter, HTTPException, Query, Path
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from sqlalchemy import desc, asc
from starlette import status

from BlogAPI.config import config_settings
from BlogAPI.db import db_session
from BlogAPI.db.SQLAlchemy_models import User, Post, Reply
from BlogAPI.pydantic_models.post_models import PostOut
from BlogAPI.pydantic_models.reply_models import ReplyOut
from BlogAPI.pydantic_models.user_models import UserIn, UserOut
from BlogAPI.util.utils import get_current_user, validate_new_user, authenticate_user

router = APIRouter()


@router.post("/user", response_model=UserOut)
def create_user(user_in: UserIn):
    """
    # Create a new user
    Just pass a username, email and password in the request body.\\
    The password is hashed, no plain text passwords are stored.\\
    Stores their info in the database.
    """
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
        return user

    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/token")
def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    # Generate token for user
    Authorizes a user for create/update/delete or for other authorization required endpoints.\\
    Can be passed to user via cookie or other method for login purposes when building a front end app.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
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


# todo - documentation for token in headers on /docs and for other auth routes
@router.get("/user/me", response_model=UserOut)
def get_me(user=Depends(get_current_user)):
    """
    # Returns current user info
    Queries database for current user information base on token provided.

    ---

    ### Authorization Header
    Must include:
    ```
    {
        "Authorization": "Bearer {token}"
    }
    ```
    """
    return user


@router.get("/user/<user-id>", response_model=UserOut)
def get_user(user_id: int):
    """
    # Returns specified users info
    Based off of user id provided
    """
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    return user


@router.get("/user/<user-id>/posts", response_model=List[PostOut])
def get_users_posts(
    user_id: int,
    skip: int = 0,
    limit: int = Query(10, ge=0, le=25),
    sort_newest_first: bool = Query(True, alias="sort-newest-first"),
):
    """
    # Returns a list of specified users posts
    Use skip and limit for pagination.\\
    Sortable by date created (by default returns newest).
    """
    session = db_session.create_session()

    if sort_newest_first:
        posts = (
            session.query(Post)
            .order_by(desc(Post.date_created))
            .filter(Post.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    else:
        posts = (
            session.query(Post)
            .order_by(asc(Post.date_created))
            .filter(Post.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    return posts


@router.get("/user/<user-id>/replies", response_model=List[ReplyOut])
def get_users_replies(
    user_id: int,
    skip: int = 0,
    limit: int = Query(10, ge=0, le=25),
    sort_newest_first: bool = Query(True, alias="sort-newest-first"),
):
    """
    # Returns a list of specified users replies
    Use skip and limit for pagination.\\
    Sortable by date created (by default returns newest).
    """
    session = db_session.create_session()

    if sort_newest_first:
        replies = (
            session.query(Reply)
            .order_by(desc(Reply.date_created))
            .filter(Reply.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    else:
        replies = (
            session.query(Reply)
            .order_by(asc(Reply.date_created))
            .filter(Reply.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    return replies


@router.post(
    "/user/follow/<user-id>",
    responses={200: {"content": {"application/json": {"example": "success"}}}},
)
def follow_user(user_id, user=Depends(get_current_user)):
    """
    # Makes current user follow specified user

    ---

    ### Authorization Header
    Must include:
    ```
    {
        "Authorization": "Bearer {token}"
    }
    ```
    """
    session = db_session.create_session()
    user_to_follow: User = session.query(User).get(user_id)

    if user in user_to_follow.followers:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User already followed",
        )

    user_to_follow.followers += [user]
    session.commit()

    return "success"


@router.get("/user/<user-id>/followers", response_model=List[UserOut])
def get_followers(user_id):
    """
    # Returns a list of all followers of current user
    """
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    return user.followers


@router.get("/user/<user-id>/following", response_model=List[UserOut])
def get_following(user_id):
    """
    # Returns a list of all users that the current user is following
    """
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    return user.following
