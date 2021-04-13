import datetime
from typing import List

from fastapi import Depends, APIRouter, HTTPException, Query
from sqlalchemy import desc
from starlette import status

from BlogAPI.db import db_session
from BlogAPI.db.SQLAlchemy_models import Post
from BlogAPI.pydantic_models.post_models import (
    NewPostIn,
    PostOut,
    UpdatePostIn,
    UpdatePostOut,
)
from BlogAPI.pydantic_models.reply_models import ReplyOut
from BlogAPI.util.utils import get_current_user

router = APIRouter()


@router.post("/post", response_model=PostOut)
def create_post(new_post: NewPostIn, user=Depends(get_current_user)):
    session = db_session.create_session()
    post = Post(
        title=new_post.title,
        body=new_post.body,
        user_id=user.id,
    )
    session.add(post)
    session.commit()
    return post


@router.put("/post/<post_id>", response_model=UpdatePostOut)
def update_post(post_id, updated_post: UpdatePostIn, user=Depends(get_current_user)):
    session = db_session.create_session()
    post = session.query(Post).get(post_id)

    if post.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This post belongs to another user",
        )

    if updated_post.title:
        post.title = updated_post.title
    if updated_post.body:
        post.body = updated_post.body

    post.date_modified = datetime.datetime.utcnow()

    session.commit()
    return post


@router.delete(
    "/post/<post_id>",
    responses={200: {"content": {"application/json": {"example": "success"}}}},
)
def delete_post(post_id, user=Depends(get_current_user)):
    session = db_session.create_session()

    try:
        post = session.query(Post).get(post_id)

        if post.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This post belongs to another user",
            )

    except AttributeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="This post does not exist"
        )

    session.delete(post)
    session.commit()
    return "success"


@router.get("/post/<post_id>", response_model=PostOut)
def get_post(post_id):
    session = db_session.create_session()
    post = session.query(Post).get(post_id)
    return post


@router.get("/post/<post_id>/replies", response_model=List[ReplyOut])
def get_replies(
    post_id: int,
    skip: int = 0,
    limit: int = Query(10, ge=0, le=25),
    sort_newest_first: bool = Query(True, alias="sort-newest-first"),
):
    session = db_session.create_session()
    post = session.query(Post).get(post_id)
    post_replies = post.replies

    if not sort_newest_first:
        post_replies.sort(key=lambda reply: reply.date_created)

    return post_replies[skip : skip + limit]


@router.get("/posts/recent", response_model=List[PostOut])
def get_recent_posts(skip: int = 0, limit: int = Query(10, ge=0, le=25)):
    session = db_session.create_session()
    posts = (
        session.query(Post)
        .order_by(desc(Post.date_created))
        .offset(skip)
        .limit(limit)
        .all()
    )

    print(posts)

    return posts
