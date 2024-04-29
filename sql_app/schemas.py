from datetime import datetime
from typing import Literal, Union

from pydantic import BaseModel, ConfigDict, FutureDatetime


class UserBase(BaseModel):
    '''Base for Pydantic user model.'''

    login: str
    project_id: int
    env: Literal['prod', 'preprod', 'stage']
    domain: Literal['canary', 'regular']
    locktime: Union[None, FutureDatetime] = None


class UserLockTime(BaseModel):
    '''Pydantic user model for setting the locktime.'''

    locktime: Union[None, FutureDatetime] = None


class UserCreate(UserBase):
    '''Pydantic user model for POST method.'''

    password: str


class User(UserBase):
    '''Pydantic user model for GET method.'''

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
