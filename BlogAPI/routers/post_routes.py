import datetime
from typing import List

from fastapi import Depends, APIRouter
from fastapi import HTTPException, Query
from sqlalchemy import desc, asc, select
from starlette import status

from BlogAPI.db.SQLAlchemy_models import Post, Reply
from BlogAPI.db.db_session_async import create_async_session
from BlogAPI.dependencies.dependencies import get_current_user
from BlogAPI.pydantic_models.post_models import (
    NewPostIn,
    PostOut,
    UpdatePostOut,
    UpdatePostIn,
)
from BlogAPI.pydantic_models.reply_models import NewReplyIn, ReplyOut

router = APIRouter()


@router.post("/post", response_model=PostOut, status_code=201)
async def create_post(
    new_post: NewPostIn,
    user=Depends(get_current_user),
):
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

    post = Post(
        title=new_post.title,
        body=new_post.body,
        user_id=user.id,
        username=user.username,
    )

    async with create_async_session() as session:
        session.add(post)
        await session.commit()
        await session.refresh(post)

    return post


@router.put(
    "/post/<post-id>",
    response_model=UpdatePostOut,
    responses={
        401: {
            "content": {
                "application/json": {
                    "example": {"detail": "This post belongs to another user"}
                }
            }
        }
    },
)
async def update_post(
    post_id,
    updated_post: UpdatePostIn,
    user=Depends(get_current_user),
):
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
    async with create_async_session() as session:
        query = select(Post).filter(Post.id == post_id)
        result = await session.execute(query)

    post = result.scalar_one_or_none()

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

    async with create_async_session() as session:
        await session.commit()

    return post


@router.delete(
    "/post/<post-id>",
    responses={
        204: {
            "content": {
                "application/json": {"example": {"detail": "Success - Post deleted"}}
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"detail": "This post belongs to another user"}
                }
            }
        },
        404: {
            "content": {
                "application/json": {"example": {"detail": "This post does not exist"}}
            }
        },
    },
    status_code=204,
)
async def delete_post(
    post_id,
    user=Depends(get_current_user),
):
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

    try:
        async with create_async_session() as session:
            query = select(Post).filter(Post.id == post_id)
            result = await session.execute(query)

        post = result.scalar_one_or_none()

        if post.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This post belongs to another user",
            )

    except AttributeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="This post does not exist"
        )

    async with create_async_session() as session:
        await session.delete(post)
        await session.commit()

    return {"detail": "success"}


@router.get("/post/<post-id>", response_model=PostOut)
async def get_post(post_id):
    """
    # Return specified post
    """
    async with create_async_session() as session:
        query = select(Post).filter(Post.id == post_id)
        result = await session.execute(query)

    post = result.scalar_one_or_none()
    return post


@router.post("/post/post-id/reply", response_model=ReplyOut, status_code=201)
async def create_reply(
    post_id: int,
    new_reply: NewReplyIn,
    user=Depends(get_current_user),
):
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

    reply = Reply(
        body=new_reply.body,
        user_id=user.id,
        username=user.username,
        post_id=post_id,
    )

    async with create_async_session() as session:
        session.add(reply)
        await session.commit()
    return reply


# noinspection DuplicatedCode
# keeping docstrings/queries as is instead of refactoring into 1 function - more readable
@router.get("/post/<post-id>/replies", response_model=List[ReplyOut])
async def get_replies(
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
    if sort_newest_first:
        sort_by = desc
    else:
        sort_by = asc

    async with create_async_session() as session:
        query = (
            select(Reply)
            .filter(Reply.post_id == post_id)
            .order_by(sort_by(Reply.date_created))
            .offset(skip)
            .limit(limit)
        )

        replies = await session.execute(query)

    return list(replies.scalars())


@router.get("/posts/recent", response_model=List[PostOut])
async def get_recent_posts(
    skip: int = 0,
    limit: int = Query(10, ge=0, le=25),
):
    """
    # Returns list of recent posts from all users
    Useful for a home/front page blog site before login
    """
    async with create_async_session() as session:
        query = select(Post).order_by(desc(Post.date_created)).offset(skip).limit(limit)

        posts = await session.execute(query)

    return list(posts.scalars())
