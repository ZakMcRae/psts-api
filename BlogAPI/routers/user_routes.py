import datetime
from typing import List

import jwt
from fastapi import Depends, APIRouter, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from sqlalchemy import desc, asc, select
from sqlalchemy.exc import IntegrityError
from starlette import status

from BlogAPI.config import config_settings
from BlogAPI.db.SQLAlchemy_models import User, Post, Reply, user_follow
from BlogAPI.db.db_session_async import create_async_session
from BlogAPI.dependencies.dependencies import get_current_user
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
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid Username or Password"}
                }
            }
        },
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


@router.post(
    "/user",
    response_model=UserOut,
    status_code=201,
    responses={
        409: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Username||Email is taken, please try another"
                    }
                }
            }
        },
    },
)
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

    # there are checks to throw status 409 within above validate_new_user
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


# noinspection DuplicatedCode
# keeping docstrings/queries as is instead of refactoring into 1 function - more readable
@router.get("/user/<user-id>/posts", response_model=List[PostOut])
async def get_users_posts(
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
    if sort_newest_first:
        sort_by = desc
    else:
        sort_by = asc

    async with create_async_session() as session:
        query = (
            select(Post)
            .filter(Post.user_id == user_id)
            .order_by(sort_by(Post.date_created))
            .offset(skip)
            .limit(limit)
        )
        posts = await session.execute(query)

    return list(posts.scalars())


# noinspection DuplicatedCode
# keeping docstrings/queries as is instead of refactoring into 1 function - more readable
@router.get("/user/<user-id>/replies", response_model=List[ReplyOut])
async def get_users_replies(
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
    if sort_newest_first:
        sort_by = desc
    else:
        sort_by = asc

    async with create_async_session() as session:
        query = (
            select(Reply)
            .filter(Reply.user_id == user_id)
            .order_by(sort_by(Reply.date_created))
            .offset(skip)
            .limit(limit)
        )

        replies = await session.execute(query)

    return list(replies.scalars())


@router.post(
    "/user/follow/<user-id>",
    responses={
        201: {
            "content": {
                "application/json": {"example": {"detail": "Success - User followed"}}
            }
        },
        409: {
            "content": {
                "application/json": {"example": {"detail": "User already followed"}}
            }
        },
    },
    status_code=201,
)
async def follow_user(user_id: int, user=Depends(get_current_user)):
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
    # try to follow user
    try:
        async with create_async_session() as session:
            stmt = user_follow.insert().values(user_id=user_id, following_id=user.id)
            await session.execute(stmt)
            await session.commit()

        return {"detail": "Success - User followed"}

    # fails on Unique constraint if user already followed
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already followed",
        )


@router.delete(
    "/user/follow/<user-id>",
    responses={
        204: {
            "content": {
                "application/json": {"example": {"detail": "Success - User unfollowed"}}
            }
        },
        404: {
            "content": {
                "application/json": {
                    "example": {"detail": "This user is not currently being followed"}
                }
            }
        },
    },
    status_code=204,
)
async def unfollow_user(user_id: int, user=Depends(get_current_user)):
    """
    # Makes current user unfollow specified user

    ---

    ### Authorization Header
    Must include:
    ```
    {
        "Authorization": "Bearer {token}"
    }
    ```
    """
    # check if actually following
    async with create_async_session() as session:
        query = select(user_follow).where(
            user_follow.c.user_id == user_id, user_follow.c.following_id == user.id
        )
        result = await session.execute(query)
        result = result.fetchall()

    if len(result) < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user is not currently being followed",
        )

    # unfollow user - deletes row in user_follow table
    async with create_async_session() as session:
        stmt = user_follow.delete().where(
            user_follow.c.user_id == user_id, user_follow.c.following_id == user.id
        )
        await session.execute(stmt)
        await session.commit()

    return {"detail": "Success - User unfollowed"}


# noinspection DuplicatedCode
# keeping docstrings/queries as is instead of refactoring into 1 function - more readable
@router.get("/user/<user-id>/followers", response_model=List[UserOut])
async def get_followers(user_id):
    """
    # Returns a list of all followers of current user
    """
    # get list of follower ids from database
    async with create_async_session() as session:
        query = select(user_follow.c.following_id).filter(
            user_follow.c.user_id == user_id
        )
        result = await session.execute(query)

    follower_ids = list(result.scalars())

    # generate list of user objects from list of ids
    async with create_async_session() as session:
        followers = []
        for follower_id in follower_ids:
            query = select(User).filter(User.id == follower_id)
            result = await session.execute(query)
            followers.append(result.scalar())

    return followers


# noinspection DuplicatedCode
# keeping docstrings/queries as is instead of refactoring into 1 function - more readable
@router.get("/user/<user-id>/following", response_model=List[UserOut])
async def get_following(user_id):
    """
    # Returns a list of all users that the current user is following
    """
    # get list of user_ids following from database
    async with create_async_session() as session:
        query = select(user_follow.c.user_id).filter(
            user_follow.c.following_id == user_id
        )
        result = await session.execute(query)

    following_ids = list(result.scalars())

    # generate list of user objects from list of ids
    async with create_async_session() as session:
        following = []
        for following_id in following_ids:
            query = select(User).filter(User.id == following_id)
            result = await session.execute(query)
            following.append(result.scalar())

    return following
