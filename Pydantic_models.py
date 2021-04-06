from pydantic import BaseModel


class UserPydantic(BaseModel):
    id: int
    username: str
