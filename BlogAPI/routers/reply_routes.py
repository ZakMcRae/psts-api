import datetime

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy import select
from starlette import status

from BlogAPI.db.SQLAlchemy_models import Reply
from BlogAPI.db.db_session_async import create_async_session
from BlogAPI.dependencies.dependencies import get_current_user
from BlogAPI.pydantic_models.reply_models import (
    UpdateReplyOut,
    UpdateReplyIn,
    ReplyOut,
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
        204: {
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
    status_code=204,
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

    return reply
