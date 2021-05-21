import datetime
from typing import List

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy import select, asc
from starlette import status

from BlogAPI.db.SQLAlchemy_models import Reply
from BlogAPI.db.db_session_async import create_async_session
from BlogAPI.dependencies.dependencies import get_current_user
from BlogAPI.pydantic_models.reply_models import (
    UpdateReplyOut,
    UpdateReplyIn,
    ReplyOut,
    Replies,
)

router = APIRouter()


@router.put(
    "/reply/{reply_id}",
    response_model=UpdateReplyOut,
    responses={
        401: {
            "content": {
                "application/json": {
                    "example": {"detail": "This reply belongs to another user"}
                }
            }
        },
    },
)
async def update_reply(
    reply_id,
    updated_reply: UpdateReplyIn,
    user=Depends(get_current_user),
):
    # docstring in markdown for OpenAPI docs
    """
    # Update specified reply
    Updates reply and stores it in the database.

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
        query = select(Reply).filter(Reply.id == reply_id)
        result = await session.execute(query)

        reply = result.scalar_one_or_none()

        # make sure reply belongs to current user
        if reply.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This reply belongs to another user",
            )

        reply.body = updated_reply.body
        reply.date_modified = datetime.datetime.utcnow()

        await session.commit()

    return reply


@router.delete(
    "/reply/{reply_id}",
    responses={
        200: {
            "content": {
                "application/json": {"example": {"detail": "Success - Reply deleted"}}
            }
        },
        401: {
            "content": {
                "application/json": {
                    "example": {"detail": "This reply belongs to another user"}
                }
            }
        },
        409: {
            "content": {
                "application/json": {"example": {"detail": "This reply does not exist"}}
            }
        },
    },
    status_code=200,
)
async def delete_reply(
    reply_id,
    user=Depends(get_current_user),
):
    """
    # Delete specified reply
    Deletes reply from the database.

    ---

    ### Authorization Header
    Must include:
    ```
    {
        "Authorization": "Bearer {token}"
    }
    ```
    """

    # make sure reply exists - goes to except if it does not
    try:
        async with create_async_session() as session:
            query = select(Reply).filter(Reply.id == reply_id)
            result = await session.execute(query)

        reply = result.scalar_one_or_none()

        # make sure reply belongs to current user
        if reply.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This reply belongs to another user",
            )

    except AttributeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="This reply does not exist"
        )

    async with create_async_session() as session:
        await session.delete(reply)
        await session.commit()

    return {"detail": "success"}


@router.get("/reply/{reply_id}", response_model=ReplyOut)
async def get_reply(reply_id):
    """
    # Return specified reply
    """
    async with create_async_session() as session:
        query = select(Reply).filter(Reply.id == reply_id)
        result = await session.execute(query)

    reply = result.scalar_one_or_none()

    if not reply:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="This reply does not exist"
        )

    return reply


@router.post(
    "/replies",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 94762,
                            "body": "Great post!",
                            "date_created": "2021-04-07 20:37:00.769100",
                            "date_modified": "null",
                            "user_id": 4376,
                            "username": "Matt",
                            "post_id": 498717,
                        },
                        {
                            "id": 94801,
                            "body": "The trip was great, can't wait to do it again!",
                            "date_created": "2021-04-08 21:29:00.849100",
                            "date_modified": "null",
                            "user_id": 3819,
                            "username": "Kim",
                            "post_id": 498904,
                        },
                    ]
                }
            }
        },
        404: {
            "content": {
                "application/json": {
                    "example": {"detail": "These replies do not exist"}
                }
            }
        },
    },
    response_model=List[ReplyOut],
)
async def get_replies_by_ids(replies: Replies):
    """# Returns all replies specified. Takes in a list of reply ids. Good for getting multiple replies in 1 query."""
    async with create_async_session() as session:
        # Pycharm warning .in_ below - functions as expected
        # noinspection PyUnresolvedReferences
        query = (
            select(Reply)
            .filter(Reply.id.in_(replies.ids))
            .order_by(asc(Reply.date_created))
        )

        replies = await session.execute(query)
        replies = list(replies.scalars())

        if not replies:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="These replies do not exist",
            )

    return replies
