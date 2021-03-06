from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NewPostIn(BaseModel):
    title: str
    body: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "title": "My First Post",
                "body": "Welcome to my blog",
            }
        }


class PostOut(BaseModel):
    id: int
    title: str
    body: str
    date_created: datetime
    date_modified: Optional[datetime]
    user_id: int
    username: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 74167,
                "title": "My First Post",
                "body": "Welcome to my blog",
                "date_created": "2021-04-07 19:41:00.769100",
                "date_modified": "null",
                "user_id": 4376,
                "username": "Matt",
            }
        }


class UpdatePostIn(BaseModel):
    title: Optional[str]
    body: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "title": "My First Updated Post",
                "body": "Welcome to my blog.",
            }
        }


class UpdatePostOut(BaseModel):
    id: int
    title: str
    body: str
    date_created: datetime
    date_modified: Optional[datetime]
    user_id: int
    username: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 74167,
                "title": "My First Updated Post",
                "body": "Welcome to my blog",
                "date_created": "2021-04-07 19:41:00.769100",
                "date_modified": "2021-04-08 19:43:00.769100",
                "user_id": 4376,
                "username": "Matt",
            }
        }
