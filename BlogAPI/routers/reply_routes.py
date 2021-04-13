import datetime

from fastapi import Depends, APIRouter, HTTPException
from starlette import status

from BlogAPI.db import db_session
from BlogAPI.db.SQLAlchemy_models import Reply
from BlogAPI.pydantic_models.reply_models import (
    ReplyOut,
    NewReplyIn,
    UpdateReplyOut,
    UpdateReplyIn,
)
from BlogAPI.util.utils import get_current_user

router = APIRouter()


@router.post("/reply", response_model=ReplyOut)
def create_reply(new_reply: NewReplyIn, user=Depends(get_current_user)):
    session = db_session.create_session()
    reply = Reply(
        body=new_reply.body,
        user_id=user.id,
    )
    session.add(reply)
    session.commit()
    return reply


@router.put("/reply/<reply_id>", response_model=UpdateReplyOut)
def update_reply(
    reply_id, updated_reply: UpdateReplyIn, user=Depends(get_current_user)
):
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
    "/reply/<reply_id>",
    responses={200: {"content": {"application/json": {"example": "success"}}}},
)
def delete_reply(reply_id, user=Depends(get_current_user)):
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


@router.get("/reply/<reply_id>", response_model=ReplyOut)
def get_reply(reply_id):
    session = db_session.create_session()
    reply = session.query(Reply).get(reply_id)
    return reply
