from datetime import datetime
from enum import Enum
from typing import Union

import bcrypt
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from . import models, schemas
from .database import AsyncSession


class QueryTypes(Enum):
    USER = 0
    ADMIN = 1


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
    users = await session.execute(select(models.User).order_by(models.User.id))
    return users.scalars().all()


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
    db_user = await get_user_admin(
        session=session,
        type=QueryTypes.USER,
        id=id,
    )
    if db_user is None:
        raise NoResultFound
    if db_user.locktime is not None and locktime is not None:
        raise ValueError
    db_user.locktime = locktime
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def create_admin(
    session: AsyncSession, admin: schemas.AdminUser
) -> models.Admin:
    '''
    Creates an admin in the database.

    Arguments:
        - AsyncSession instance.
        - sql_app.schemas.UserCreate Pydantic model.

    A created admin is returned.
    '''
    db_admin = models.Admin(
        login=admin.login,
        password=bcrypt.hashpw(admin.password, bcrypt.gensalt()),
    )
    session.add(db_admin)
    await session.commit()
    await session.refresh(db_admin)
    return db_admin


async def create_first_admin(
    session: AsyncSession, login: str, password: str
) -> models.Admin:
    '''
    Creates a superuser in the database.

    Arguments:
        - AsyncSession instance.
        - login.
        - password.

    A created admin is returned.
    '''
    first_db_admin = await get_user_admin(
        session=session,
        type=QueryTypes.ADMIN,
        login=login,
    )
    if first_db_admin is None:
        first_db_admin = models.Admin(
            login=login,
            password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()),
        )
        session.add(first_db_admin)
        await session.commit()
        await session.refresh(first_db_admin)
    return first_db_admin


async def get_user_admin(
    session: AsyncSession,
    type: int,
    id: Union[int, None] = None,
    login: str = None,
) -> Union[models.User, models.Admin]:
    '''
    function that queries a single Admin/User instance.

    Arguments:
        - AsyncSession instance.
        - type of desired instance (Admin/User).
        - id.
        - login.

    Returns an Admin or User instance
    '''
    if type == QueryTypes.ADMIN:
        if id is not None:
            user_admin = await session.execute(
                select(models.Admin).filter(models.Admin.id == id)
            )
        elif login is not None:
            user_admin = await session.execute(
                select(models.Admin).filter(models.Admin.login == login)
            )
    elif type == QueryTypes.USER:
        if id is not None:
            user_admin = await session.execute(
                select(models.User).filter(models.User.id == id)
            )
        elif login is not None:
            user_admin = await session.execute(
                select(models.User).filter(models.User.login == login)
            )
    return user_admin.scalar_one_or_none()
