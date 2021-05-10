from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NewReplyIn(BaseModel):
    body: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "body": "Great post!",
            }
        }


class ReplyOut(BaseModel):
    id: int
    body: str
    date_created: datetime
    date_modified: Optional[datetime]
    user_id: int
    username: str
    post_id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 94762,
                "body": "Great post!",
                "date_created": "2021-04-07 20:37:00.769100",
                "date_modified": "null",
                "user_id": 4376,
                "username": "Matt",
                "post_id": 498717,
            }
        }


class UpdateReplyIn(BaseModel):
    body: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "body": "Great post! Can't wait to hear more.",
            }
        }


class UpdateReplyOut(BaseModel):
    id: int
    body: str
    date_created: datetime
    date_modified: Optional[datetime]
    user_id: int
    username: str
    post_id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 94762,
                "body": "Great post! Can't wait to hear more.",
                "date_created": "2021-04-07 20:37:00.769100",
                "date_modified": "2021-04-09 14:16:00.769100",
                "user_id": 4376,
                "username": "Matt",
                "post_id": 498717,
            }
        }
