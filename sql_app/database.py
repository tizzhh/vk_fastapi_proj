import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv('URL')

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()


async def get_session():
    '''Dependency session.'''
    async with async_session() as session:
        yield session
