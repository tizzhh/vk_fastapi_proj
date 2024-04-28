from datetime import datetime
from typing import Literal, Union

from pydantic import BaseModel


class UserBase(BaseModel):
    login: str
    project_id: int
    env: Literal['prod', 'preprod', 'stage']
    domain: Literal['canary', 'regular']


class UserCreate(UserBase):
    password: str
    locktime: Union[None, datetime]


class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
