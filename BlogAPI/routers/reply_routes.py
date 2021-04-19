import datetime

from fastapi import Depends, APIRouter, HTTPException
from starlette import status

from BlogAPI.db import db_session
from BlogAPI.db.SQLAlchemy_models import Reply
from BlogAPI.pydantic_models.reply_models import (
    ReplyOut,
    UpdateReplyOut,
    UpdateReplyIn,
)
from BlogAPI.util.utils import get_current_user

router = APIRouter()


@router.put("/reply/<reply-id>", response_model=UpdateReplyOut)
def update_reply(
    reply_id, updated_reply: UpdateReplyIn, user=Depends(get_current_user)
):
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
    session = db_session.create_session()
    reply = session.query(Reply).get(reply_id)

    if reply.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This reply belongs to another user",
        )

    reply.body = updated_reply.body
    reply.date_modified = datetime.datetime.utcnow()

    session.commit()
    return reply


@router.delete(
    "/reply/<reply-id>",
    responses={200: {"content": {"application/json": {"example": "success"}}}},
)
def delete_reply(reply_id, user=Depends(get_current_user)):
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
    session = db_session.create_session()

    try:
        reply = session.query(Reply).get(reply_id)

        if reply.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This reply belongs to another user",
            )

    except AttributeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="This reply does not exist"
        )

    session.delete(reply)
    session.commit()
    return "success"


@router.get("/reply/<reply-id>", response_model=ReplyOut)
def get_reply(reply_id):
    """
    # Return specified reply
    """
    session = db_session.create_session()
    reply = session.query(Reply).get(reply_id)
    return reply
