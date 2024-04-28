from datetime import datetime
from typing import Literal, Union

from pydantic import BaseModel


class UserBase(BaseModel):
    '''Base for Pydantic user model.'''

    login: str
    project_id: int
    env: Literal['prod', 'preprod', 'stage']
    domain: Literal['canary', 'regular']


class UserCreate(UserBase):
    '''Pydantic user model for POST method.'''

    password: str
    locktime: Union[None, datetime] = None


class User(UserBase):
    '''Pydantic user model for GET method.'''

    id: int
    created_at: datetime

    class Config:
        orm_mode = True
