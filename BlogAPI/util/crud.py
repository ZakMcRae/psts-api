from sqlalchemy.orm import Session
from BlogAPI.pydantic_models import user_models, post_models, reply_models
from BlogAPI.db.SQLAlchemy_models import User, Post, Reply
from BlogAPI.pydantic_models.user_models import UserIn
from BlogAPI.util.utils import validate_new_user
from passlib.hash import bcrypt


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserIn):
    if validate_new_user(user.username, user.email):
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


# todo - add rest of crud operations
# take queries from endpoints
# move into these functions

# can more simply overwrite dependencies for testing
