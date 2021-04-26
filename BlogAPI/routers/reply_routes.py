import datetime

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from BlogAPI.db.SQLAlchemy_models import Reply
from BlogAPI.dependencies.dependencies import get_current_user, get_db
from BlogAPI.pydantic_models.reply_models import (
    UpdateReplyOut,
    UpdateReplyIn,
    ReplyOut,
)

router = APIRouter()


@router.put("/reply/<reply-id>", response_model=UpdateReplyOut)
def update_reply(
    reply_id,
    updated_reply: UpdateReplyIn,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
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

    reply = db.query(Reply).get(reply_id)

    # make sure reply belongs to current user
    if reply.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This reply belongs to another user",
        )

    reply.body = updated_reply.body
    reply.date_modified = datetime.datetime.utcnow()

    db.commit()
    return reply


@router.delete(
    "/reply/<reply-id>",
    responses={
        200: {"content": {"application/json": {"example": {"detail": "success"}}}}
    },
)
def delete_reply(
    reply_id,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
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
        reply = db.query(Reply).get(reply_id)

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

    db.delete(reply)
    db.commit()
    return {"detail": "success"}


@router.get("/reply/<reply-id>", response_model=ReplyOut)
def get_reply(reply_id, db: Session = Depends(get_db)):
    """
    # Return specified reply
    """

    reply = db.query(Reply).get(reply_id)
    return reply
