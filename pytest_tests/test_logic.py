import json
from datetime import datetime, timedelta
from http import HTTPStatus

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_users_acquire_lock_already_locked(
    async_client: AsyncClient,
    async_session: AsyncSession,
    create_user,
    token: str,
):
    LOCKTIME = datetime.now() + timedelta(days=1)
    LOCKTIME = LOCKTIME.strftime('%Y-%m-%d')
    data = {'locktime': LOCKTIME}
    data = json.dumps(data)
    await async_client.patch(
        '/users/1/acquire_lock',
        content=data,
        headers={'Authorization': 'Bearer ' + token},
    )
    response = await async_client.patch(
        '/users/1/acquire_lock',
        content=data,
        headers={'Authorization': 'Bearer ' + token},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_user_already_exists(
    async_client: AsyncClient,
    async_session: AsyncSession,
    create_user,
    token: str,
):
    data = {
        'login': 'aboba',
        'project_id': 1,
        'env': 'prod',
        'domain': 'canary',
        'password': '1234',
    }
    data = json.dumps(data)
    response = await async_client.post(
        '/users', content=data, headers={'Authorization': 'Bearer ' + token}
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_admin_already_exists(
    async_client: AsyncClient,
    async_session: AsyncSession,
    create_user,
    token: str,
):
    data = {
        'login': 'admin',
        'password': 'admin',
    }
    data = json.dumps(data)
    await async_client.post(
        '/admins', content=data, headers={'Authorization': 'Bearer ' + token}
    )
    response = await async_client.post(
        '/admins', content=data, headers={'Authorization': 'Bearer ' + token}
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_token_wrong_credentials(
    async_client: AsyncClient,
    async_session: AsyncSession,
):
    await async_client.post('/superuser')
    data = {'username': "a", 'password': "a"}
    response_token = await async_client.post('/token', data=data)
    assert response_token.status_code == HTTPStatus.UNAUTHORIZED
