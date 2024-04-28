from datetime import datetime

from sqlalchemy import select

from . import models, schemas
from .database import AsyncSession


async def create_user(
    db: AsyncSession, user: schemas.UserCreate
) -> models.User:
    '''
    Creates a user in the database.

    Arguments:
        - AsyncSession instance.
        - sql_app.schemas.UserCreate Pydantic model.

    A created user is returned.
    '''
    db_user = models.User(
        login=user.login,
        password=user.password,
        env=user.env,
        domain=user.domain,
        project_id=user.project_id,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_users(db: AsyncSession) -> list[models.User]:
    '''
    Gets all users from the database.

    Arguments:
        - AsyncSession instance.

    A list of users is returned.
    '''
    result = await db.execute(select(models.User))
    result = result.scalars().all()
    return result


async def acquire_lock(db: AsyncSession, locktime: datetime, id: int):
    db_user = await db.execute(
        select(models.User).filter(models.User.id == id)
    )
    db_user = db_user.first()
    db_user.locktime = locktime
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def release_lock(db: AsyncSession, id: int):
    db_user = await db.execute(
        select(models.User).filter(models.User.id == id)
    )
    db_user = db_user.first()
    db_user.locktime = None
    await db.commit()
    await db.refresh(db_user)
    return db_user
