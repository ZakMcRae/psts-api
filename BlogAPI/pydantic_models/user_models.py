from typing import Optional

from pydantic import BaseModel, EmailStr, constr, conint


class UserIn(BaseModel):
    username: constr(min_length=3, max_length=24)
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "username": "Matt",
                "email": "matt@example.com",
                "password": "password",
            }
        }


class UserOut(BaseModel):
    username: str
    email: EmailStr
    id: Optional[int] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 4376,
                "username": "Matt",
                "email": "matt@example.com",
            }
        }


class UserItemList(BaseModel):
    skip: Optional[conint(ge=0)] = 0
    limit: Optional[conint(ge=0, le=100)] = 10
    sort_newest_first: Optional[bool] = True

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "skip": 0,
                "limit": 10,
                "sort_newest_first": True,
            }
        }
