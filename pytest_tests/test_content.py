import json
from datetime import datetime, timedelta
from http import HTTPStatus

import bcrypt
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from pytest_tests.conftest import ADMIN0_LOGIN, ADMIN0_PASSWORD

# from pytest_tests.conftest import MethodType


# @pytest.mark.parametrize(
#     'method_type, status_code'
#     [
#         (
#             MethodType.GET,
#             HTTPStatus.OK,
#         ),
#         (
#             MethodType.POST,
#             HTTPStatus.CREATED,
#         )
#     ],
# )
# @pytest.mark.asyncio
# async def test_users_create_retrieve(

# )

EXPECTED_RESPONSE_USERS_CREATE_RETRIEVE = {
    'login': 'aboba',
    'project_id': 1,
    'env': 'prod',
    'domain': 'canary',
    'locktime': None,
    'password': '1234',
    'id': 1,
}
EXPECTED_USER_KEYS = [key for key in EXPECTED_RESPONSE_USERS_CREATE_RETRIEVE]


@pytest.mark.asyncio
async def test_superuser_create(
    async_client: AsyncClient,
    async_session: AsyncSession,
):
    response = await async_client.post('/superuser')
    assert response.status_code == HTTPStatus.CREATED
    response_body = response.json()
    assert 'login' in response_body
    assert 'password' in response_body
    assert response_body['login'] == ADMIN0_LOGIN
    # assert bcrypt.checkpw(bytes(response_body['password'].encode('utf-8').hex(), 'utf-8'), ADMIN0_PASSWORD.encode('utf-8'))


@pytest.mark.asyncio
async def test_users_retrieve(
    async_client: AsyncClient,
    async_session: AsyncSession,
    create_user,
    token: str,
):
    response = await async_client.get(
        '/users', headers={'Authorization': 'Bearer ' + token}
    )
    assert response.status_code == HTTPStatus.OK
    response_body = response.json()
    assert len(response_body) == 1
    retrieved_user = response_body[0]
    for key in EXPECTED_USER_KEYS:
        assert key in retrieved_user
        assert (
            retrieved_user[key] == EXPECTED_RESPONSE_USERS_CREATE_RETRIEVE[key]
        )
    assert 'created_at' in retrieved_user
    assert datetime.strptime(
        retrieved_user['created_at'], '%Y-%m-%dT%H:%M:%S.%f'
    ).replace(second=0, microsecond=0) == datetime.now().replace(
        second=0, microsecond=0
    )


@pytest.mark.asyncio
async def test_user_create(
    async_client: AsyncClient,
    async_session: AsyncSession,
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

    assert response.status_code == HTTPStatus.CREATED
    response_body = response.json()
    for key in EXPECTED_USER_KEYS:
        assert key in response_body
        assert (
            response_body[key] == EXPECTED_RESPONSE_USERS_CREATE_RETRIEVE[key]
        )
    assert 'created_at' in response_body
    assert datetime.strptime(
        response_body['created_at'], '%Y-%m-%dT%H:%M:%S.%f'
    ).replace(second=0, microsecond=0) == datetime.now().replace(
        second=0, microsecond=0
    )


@pytest.mark.asyncio
async def test_users_acquire_lock(
    async_client: AsyncClient,
    async_session: AsyncSession,
    create_user,
    token: str,
):
    LOCKTIME = datetime.now() + timedelta(days=1)
    LOCKTIME = LOCKTIME.strftime('%Y-%m-%d')
    data = {'locktime': LOCKTIME}
    json_data = json.dumps(data)
    response = await async_client.patch(
        '/users/1/acquire_lock',
        content=json_data,
        headers={'Authorization': 'Bearer ' + token},
    )
    assert response.status_code == HTTPStatus.OK
    response_body = response.json()
    assert 'locktime' in response_body
    assert datetime.strptime(
        response_body['locktime'], '%Y-%m-%dT%H:%M:%S'
    ) == datetime.strptime(LOCKTIME, '%Y-%m-%d')
    exp_user_keys = [key for key in EXPECTED_USER_KEYS if key != 'locktime']
    for key in exp_user_keys:
        assert key in response_body
        assert (
            response_body[key] == EXPECTED_RESPONSE_USERS_CREATE_RETRIEVE[key]
        )
    assert 'created_at' in response_body
    assert datetime.strptime(
        response_body['created_at'], '%Y-%m-%dT%H:%M:%S.%f'
    ).replace(second=0, microsecond=0) == datetime.now().replace(
        second=0, microsecond=0
    )


@pytest.mark.asyncio
async def test_users_release_lock(
    async_client: AsyncClient,
    async_session: AsyncSession,
    create_user,
    token: str,
):
    response = await async_client.patch(
        '/users/1/release_lock', headers={'Authorization': 'Bearer ' + token}
    )
    assert response.status_code == HTTPStatus.OK
    response_body = response.json()
    for key in EXPECTED_USER_KEYS:
        assert key in response_body
        assert (
            response_body[key] == EXPECTED_RESPONSE_USERS_CREATE_RETRIEVE[key]
        )
    assert 'created_at' in response_body
    assert datetime.strptime(
        response_body['created_at'], '%Y-%m-%dT%H:%M:%S.%f'
    ).replace(second=0, microsecond=0) == datetime.now().replace(
        second=0, microsecond=0
    )


@pytest.mark.asyncio
async def test_admin_create(
    async_client: AsyncClient,
    async_session: AsyncSession,
    token: str,
):
    data = {
        'login': 'admin',
        'password': 'admin',
    }
    data = json.dumps(data)
    response = await async_client.post(
        '/admins', content=data, headers={'Authorization': 'Bearer ' + token}
    )
    assert response.status_code == HTTPStatus.CREATED
    response_body = response.json()
    assert 'login' in response_body
    assert 'password' in response_body
