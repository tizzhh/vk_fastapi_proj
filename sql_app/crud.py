from datetime import datetime

from sqlalchemy import select

from . import models, schemas
from .database import AsyncSession


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    db_user = models.User(**user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


async def get_users(db: AsyncSession):
    result = await db.execute(select(models.User))
    result = result.scalars().all()
    return result


async def acquire_lock(db: AsyncSession, locktime: datetime, user_id: int):
    db_user = await db.execute(
        select(models.User).filter(models.User.user_id == user_id)
    )
    db_user = db_user.first()
    db_user.locktime = locktime
    db.commit()
    db.refresh(db_user)
    return db_user


async def release_lock(db: AsyncSession, user_id: int):
    db_user = await db.execute(
        select(models.User).filter(models.User.user_id == user_id)
    )
    db_user = db_user.first()
    db_user.locktime = None
    db.commit()
    db.refresh(db_user)
    return db_user
