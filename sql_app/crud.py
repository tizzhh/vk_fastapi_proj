from datetime import datetime
from typing import Union

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from . import models, schemas
from .database import AsyncSession


async def create_user(
    session: AsyncSession, user: schemas.UserCreate
) -> models.User:
    '''
    Creates a user in the database.

    Arguments:
        - AsyncSession instance.
        - sql_app.schemas.UserCreate Pydantic model.

    A created user is returned.
    '''
    db_user = models.User(**user.model_dump())
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def get_users(session: AsyncSession) -> list[models.User]:
    '''
    Gets all users from the database.

    Arguments:
        - AsyncSession instance.

    A list of users is returned.
    '''
    users = await session.execute(select(models.User))
    users = users.scalars().all()
    return users


async def acquire_release_lock(
    session: AsyncSession, locktime: Union[datetime, None], id: int
) -> models.User:
    '''
    Sets user's locktime to a datetime or a null value.

    Arguments:
        - AsyncSession instance.
        - Locktime: datetime or null.
        - id: User's id.

    User with specified id and modified locktime is returned.
    '''
    db_user = await session.execute(
        select(models.User).filter(models.User.id == id)
    )
    db_user = db_user.scalar_one()
    if db_user is None:
        raise NoResultFound
    if db_user.locktime is not None and locktime is not None:
        raise ValueError
    db_user.locktime = locktime
    await session.commit()
    await session.refresh(db_user)
    return db_user
