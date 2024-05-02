import json
import os
from enum import Enum

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from main import app
from sql_app.database import Base, engine

load_dotenv()

ADMIN0_LOGIN = os.getenv('ADMIN0LOGIN')
ADMIN0_PASSWORD = os.getenv('ADMIN0PASSWORD')


class MethodType(Enum):
    GET = 0
    POST = 1
    PUT = 2
    PATCH = 3


@pytest.fixture(scope='session')
def setup_database():
    alembic_cfg = Config('alembic_tests.ini')
    command.upgrade(alembic_cfg, 'head')


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test',
    ) as client:
        yield client


@pytest_asyncio.fixture(scope='function')
async def async_session():
    session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session() as s:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield s

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope='function')
async def token(async_client):
    reponse = await async_client.post('/superuser')
    data = {'username': ADMIN0_LOGIN, 'password': ADMIN0_PASSWORD}
    reponse = await async_client.post('/token', data=data)
    return reponse.json()['access_token']


@pytest_asyncio.fixture(scope='function')
async def create_user(async_client, token):
    data = {
        'login': 'aboba',
        'project_id': 1,
        'env': 'prod',
        'domain': 'canary',
        'password': '1234',
    }
    data = json.dumps(data)
    await async_client.post(
        '/users', content=data, headers={'Authorization': 'Bearer ' + token}
    )
