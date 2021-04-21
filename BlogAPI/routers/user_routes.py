import datetime

import jwt
from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

import BlogAPI.util.crud as crud
from BlogAPI.config import config_settings
from BlogAPI.db.SQLAlchemy_models import User
from BlogAPI.dependencies.dependencies import get_db
from BlogAPI.pydantic_models.user_models import UserOut, UserIn
from BlogAPI.util.utils import authenticate_user, validate_new_user

router = APIRouter()


@router.post("/token")
def generate_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    # Generate token for user
    Authorizes a user for create/update/delete or for other authorization required endpoints.\\
    Can be passed to user via cookie or other method for login purposes when building a front end app.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
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
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    # Returns specified user
    Based off of user id provided
    """
    return crud.read_user(db, user_id)


@router.post("/user", response_model=UserOut)
def create_user(user_in: UserIn, db: Session = Depends(get_db)):
    """
    # Create new user
    The password is hashed, no plain text passwords are stored.\\
    Stores user info in the database.
    """
    return crud.create_user(db, user_in)


# @router.get("/user/me", response_model=UserOut)
# def get_me(user=Depends(get_current_user)):
#     """
#     # Returns current user info
#     Queries database for current user information base on token provided.
#
#     ---
#
#     ### Authorization Header
#     Must include:
#     ```
#     {
#         "Authorization": "Bearer {token}"
#     }
#     ```
#     """
#     return user


# @router.get("/user/<user-id>/posts", response_model=List[PostOut])
# def get_users_posts(
#     user_id: int,
#     skip: int = 0,
#     limit: int = Query(10, ge=0, le=25),
#     sort_newest_first: bool = Query(True, alias="sort-newest-first"),
# ):
#     """
#     # Returns a list of specified users posts
#     Use skip and limit for pagination.\\
#     Sortable by date created (by default returns newest).
#     """
#     session = db_session.create_session()
#
#     if sort_newest_first:
#         posts = (
#             session.query(Post)
#             .order_by(desc(Post.date_created))
#             .filter(Post.user_id == user_id)
#             .offset(skip)
#             .limit(limit)
#             .all()
#         )
#
#     else:
#         posts = (
#             session.query(Post)
#             .order_by(asc(Post.date_created))
#             .filter(Post.user_id == user_id)
#             .offset(skip)
#             .limit(limit)
#             .all()
#         )
#
#     return posts
#
#
# @router.get("/user/<user-id>/replies", response_model=List[ReplyOut])
# def get_users_replies(
#     user_id: int,
#     skip: int = 0,
#     limit: int = Query(10, ge=0, le=25),
#     sort_newest_first: bool = Query(True, alias="sort-newest-first"),
# ):
#     """
#     # Returns a list of specified users replies
#     Use skip and limit for pagination.\\
#     Sortable by date created (by default returns newest).
#     """
#     session = db_session.create_session()
#
#     if sort_newest_first:
#         replies = (
#             session.query(Reply)
#             .order_by(desc(Reply.date_created))
#             .filter(Reply.user_id == user_id)
#             .offset(skip)
#             .limit(limit)
#             .all()
#         )
#
#     else:
#         replies = (
#             session.query(Reply)
#             .order_by(asc(Reply.date_created))
#             .filter(Reply.user_id == user_id)
#             .offset(skip)
#             .limit(limit)
#             .all()
#         )
#
#     return replies
#
#
# @router.post(
#     "/user/follow/<user-id>",
#     responses={200: {"content": {"application/json": {"example": "success"}}}},
# )
# def follow_user(user_id, user=Depends(get_current_user)):
#     """
#     # Makes current user follow specified user
#
#     ---
#
#     ### Authorization Header
#     Must include:
#     ```
#     {
#         "Authorization": "Bearer {token}"
#     }
#     ```
#     """
#     session = db_session.create_session()
#     user_to_follow: User = session.query(User).get(user_id)
#
#     if user in user_to_follow.followers:
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail="User already followed",
#         )
#
#     user_to_follow.followers += [user]
#     session.commit()
#
#     return "success"
#
#
# @router.get("/user/<user-id>/followers", response_model=List[UserOut])
# def get_followers(user_id):
#     """
#     # Returns a list of all followers of current user
#     """
#     session = db_session.create_session()
#     user = session.query(User).get(user_id)
#     return user.followers
#
#
# @router.get("/user/<user-id>/following", response_model=List[UserOut])
# def get_following(user_id):
#     """
#     # Returns a list of all users that the current user is following
#     """
#     session = db_session.create_session()
#     user = session.query(User).get(user_id)
#     return user.following
