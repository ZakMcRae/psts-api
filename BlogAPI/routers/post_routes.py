import datetime
from typing import List

from fastapi import Depends, APIRouter, HTTPException, Query
from sqlalchemy import desc, asc
from starlette import status

from BlogAPI.db import db_session
from BlogAPI.db.SQLAlchemy_models import Post, Reply
from BlogAPI.pydantic_models.post_models import (
    NewPostIn,
    PostOut,
    UpdatePostIn,
    UpdatePostOut,
)
from BlogAPI.pydantic_models.reply_models import ReplyOut, NewReplyIn
from BlogAPI.util.utils import get_current_user

router = APIRouter()


@router.post("/post", response_model=PostOut)
def create_post(new_post: NewPostIn, user=Depends(get_current_user)):
    """
    # Create a new post
    Stores post into database.

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
    post = Post(
        title=new_post.title,
        body=new_post.body,
        user_id=user.id,
        username=user.username,
    )
    session.add(post)
    session.commit()
    return post


@router.put("/post/<post-id>", response_model=UpdatePostOut)
def update_post(post_id, updated_post: UpdatePostIn, user=Depends(get_current_user)):
    """
    # Update specified post
    Updates post into database.

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
    "/post/<post-id>",
    responses={200: {"content": {"application/json": {"example": "success"}}}},
)
def delete_post(post_id, user=Depends(get_current_user)):
    """
    # Delete specified post
    Deletes post and all replies to the post from the database.

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


@router.get("/post/<post-id>", response_model=PostOut)
def get_post(post_id):
    """
    # Return specified post
    """
    session = db_session.create_session()
    post = session.query(Post).get(post_id)
    return post


@router.post("/post/post-id/reply", response_model=ReplyOut)
def create_reply(post_id: int, new_reply: NewReplyIn, user=Depends(get_current_user)):
    """
    # Create new reply
    Creates reply to specified post and stores it in the database.

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
    reply = Reply(
        body=new_reply.body,
        user_id=user.id,
        username=user.username,
        post_id=post_id,
    )
    session.add(reply)
    session.commit()
    return reply


@router.get("/post/<post-id>/replies", response_model=List[ReplyOut])
def get_replies(
    post_id: int,
    skip: int = 0,
    limit: int = Query(10, ge=0, le=25),
    sort_newest_first: bool = Query(True, alias="sort-newest-first"),
):
    """
    # Returns all replies to specified post
    Use skip and limit for pagination.\\
    Sortable by date created (by default returns newest).
    """
    session = db_session.create_session()

    if sort_newest_first:
        replies = (
            session.query(Reply)
            .order_by(desc(Reply.date_created))
            .filter(Reply.post_id == post_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    else:
        replies = (
            session.query(Reply)
            .order_by(asc(Reply.date_created))
            .filter(Reply.post_id == post_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    return replies


@router.get("/posts/recent", response_model=List[PostOut])
def get_recent_posts(skip: int = 0, limit: int = Query(10, ge=0, le=25)):
    """
    # Returns list of recent posts from all users
    Useful for a home/front page blog site before login
    """
    session = db_session.create_session()
    posts = (
        session.query(Post)
        .order_by(desc(Post.date_created))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return posts
