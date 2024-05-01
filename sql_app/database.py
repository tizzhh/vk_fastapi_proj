import os
import sys

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# CHANGE BACK TO URL
DATABASE_URL = os.getenv('URL')
if 'pytest' in sys.modules:
    DATABASE_URL = os.getenv('TEST_DB')

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()


async def get_session():
    '''Dependency session.'''
    async with async_session() as session:
        yield session
