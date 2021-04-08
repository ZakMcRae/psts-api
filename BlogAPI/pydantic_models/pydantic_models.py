from typing import Optional

from pydantic import BaseModel, EmailStr, constr


class UserIn(BaseModel):
    username: constr(min_length=3, max_length=24)
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "username": "zak",
                "email": "zak@example.com",
                "password": "123456",
            }
        }


class UserOut(BaseModel):
    id: Optional[int] = None
    username: str
    email: EmailStr

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "username": "zak",
                "email": "zak@example.com",
            }
        }
