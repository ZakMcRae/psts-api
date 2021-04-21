from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from BlogAPI.pydantic_models import user_models, post_models, reply_models
from BlogAPI.db.SQLAlchemy_models import User, Post, Reply
from BlogAPI.pydantic_models.user_models import UserIn
from BlogAPI.util.utils import validate_new_user
from passlib.hash import bcrypt


def read_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserIn):
    if validate_new_user(db, user.username, user.email):
        hs_password = bcrypt.hash(user.password)
        user = User(
            username=user.username,
            email=user.email,
            hs_password=hs_password,
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
