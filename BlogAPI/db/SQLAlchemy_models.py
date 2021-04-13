import datetime
from typing import Optional, List

import sqlalchemy as sa
import sqlalchemy.orm as orm
from passlib.hash import bcrypt
from sqlalchemy.ext.declarative import declarative_base

SQLAlchemyBase = declarative_base()


class Reply(SQLAlchemyBase):
    __tablename__ = "replies"

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    body: str = sa.Column(sa.TEXT, nullable=False)
    date_created: datetime = sa.Column(
        sa.DATETIME,
        nullable=False,
        default=datetime.datetime.utcnow,
    )
    date_modified: datetime = sa.Column(sa.DATETIME)
    user_id = sa.Column(sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    username = sa.Column(
        sa.ForeignKey("users.username", ondelete="CASCADE"), nullable=False
    )
    post_id = sa.Column(sa.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)

    def __eq__(self, other):
        return self.id == other.id


class Post(SQLAlchemyBase):
    __tablename__ = "posts"

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title: str = sa.Column(sa.String, nullable=False)
    body: str = sa.Column(sa.TEXT, nullable=False)
    date_created: datetime = sa.Column(
        sa.DATETIME,
        nullable=False,
        default=datetime.datetime.utcnow,
    )
    date_modified: datetime = sa.Column(sa.DATETIME)
    user_id = sa.Column(sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    username = sa.Column(
        sa.ForeignKey("users.username", ondelete="CASCADE"), nullable=False
    )
    replies: Optional[List[Reply]] = orm.relationship(
        "Reply",
        order_by="desc(Reply.date_created)",
        cascade="all,delete-orphan",
    )

    def __eq__(self, other):
        return self.id == other.id


class User(SQLAlchemyBase):
    __tablename__ = "users"

    id: int = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    username: str = sa.Column(sa.String(24), unique=True, nullable=False)
    email: str = sa.Column(sa.String(120), unique=True, nullable=False)
    hs_password: str = sa.Column(sa.String(60), nullable=False)
    posts: Optional[List[Post]] = orm.relationship(
        "Post",
        order_by="desc(Post.date_created)",
        cascade="all,delete-orphan",
        foreign_keys="[Post.user_id]",
    )
    replies: Optional[List[Reply]] = orm.relationship(
        "Reply",
        order_by="desc(Reply.date_created)",
        cascade="all,delete-orphan",
        foreign_keys="[Reply.user_id]",
    )
    following = orm.relationship(
        "User",
        lambda: user_follow,
        primaryjoin=lambda: User.id == user_follow.c.user_id,
        secondaryjoin=lambda: User.id == user_follow.c.following_id,
        backref="followers",
    )

    def verify_password(self, password):
        return bcrypt.verify(password, self.hs_password)

    def __repr__(self):
        return f"user:{self.username}, id:{self.id}"

    def __eq__(self, other):
        return self.id == other.id


user_follow = sa.Table(
    "user_follow",
    SQLAlchemyBase.metadata,
    sa.Column("user_id", sa.Integer, sa.ForeignKey(User.id), primary_key=True),
    sa.Column("following_id", sa.Integer, sa.ForeignKey(User.id), primary_key=True),
)
