import datetime
from typing import List

import jwt
from fastapi import Depends, APIRouter, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from sqlalchemy import desc, asc, select
from sqlalchemy.orm import Session
from starlette import status

from BlogAPI.config import config_settings
from BlogAPI.db.SQLAlchemy_models import User, Post, Reply
from BlogAPI.db.db_session_async import create_async_session
from BlogAPI.dependencies.dependencies import get_db, get_current_user
from BlogAPI.pydantic_models.post_models import PostOut
from BlogAPI.pydantic_models.reply_models import ReplyOut
from BlogAPI.pydantic_models.user_models import UserOut, UserIn
from BlogAPI.util.utils import authenticate_user, validate_new_user

router = APIRouter()


@router.post(
    "/token",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"access_token": "token", "token_type": "bearer"}
                }
            }
        }
    },
)
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    # Generate token for user
    Authorizes a user for create/update/delete or for other authorization required endpoints.\\
    Can be passed to user via cookie or other method for login purposes when building a front end app.
    """
    user = await authenticate_user(form_data.username, form_data.password)
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


@router.get("/user/<user-id>", response_model=UserOut)
async def get_user(user_id: int):
    """
    # Returns specified user
    Based off of user id provided
    """
    async with create_async_session() as session:
        query = select(User).filter(User.id == user_id)
        result = await session.execute(query)

    return result.scalar_one_or_none()


@router.post("/user", response_model=UserOut)
async def create_user(user_in: UserIn):
    """
    # Create new user
    The password is hashed, no plain text passwords are stored.\\
    Stores user info in the database.
    """
    # make sure username and email unique
    if await validate_new_user(user_in.username, user_in.email):
        hs_password = bcrypt.hash(user_in.password)
        user = User(
            username=user_in.username,
            email=user_in.email,
            hs_password=hs_password,
        )

    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # store user in database
    async with create_async_session() as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


@router.get("/user/me", response_model=UserOut)
async def get_me(user=Depends(get_current_user)):
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


@router.get("/user/<user-id>/posts", response_model=List[PostOut])
def get_users_posts(
    user_id: int,
    skip: int = 0,
    limit: int = Query(10, ge=0, le=25),
    sort_newest_first: bool = Query(True, alias="sort-newest-first"),
    db: Session = Depends(get_db),
):
    """
    # Returns a list of specified users posts
    Use skip and limit for pagination.\\
    Sortable by date created (by default returns newest).
    """
    if sort_newest_first:
        posts = (
            db.query(Post)
            .order_by(desc(Post.date_created))
            .filter(Post.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    else:
        posts = (
            db.query(Post)
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
    db: Session = Depends(get_db),
):
    """
    # Returns a list of specified users replies
    Use skip and limit for pagination.\\
    Sortable by date created (by default returns newest).
    """
    if sort_newest_first:
        replies = (
            db.query(Reply)
            .order_by(desc(Reply.date_created))
            .filter(Reply.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    else:
        replies = (
            db.query(Reply)
            .order_by(asc(Reply.date_created))
            .filter(Reply.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    return replies


@router.post(
    "/user/follow/<user-id>",
    responses={
        200: {"content": {"application/json": {"example": {"detail": "success"}}}}
    },
)
def follow_user(user_id, user=Depends(get_current_user), db: Session = Depends(get_db)):
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
    user_to_follow: User = db.query(User).get(user_id)

    if user in user_to_follow.followers:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already followed",
        )

    user_to_follow.followers += [user]
    db.commit()

    return {"detail": "success"}


@router.get("/user/<user-id>/followers", response_model=List[UserOut])
def get_followers(user_id, db: Session = Depends(get_db)):
    """
    # Returns a list of all followers of current user
    """
    user = db.query(User).get(user_id)
    return user.followers


@router.get("/user/<user-id>/following", response_model=List[UserOut])
def get_following(user_id, db: Session = Depends(get_db)):
    """
    # Returns a list of all users that the current user is following
    """
    user = db.query(User).get(user_id)
    return user.following
