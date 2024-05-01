from enum import Enum
from http import HTTPStatus

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from pytest_tests.conftest import ADMIN0_LOGIN, ADMIN0_PASSWORD, MethodType

URLS_METHOD_TYPES = {
    'users': MethodType.GET,
    'users_post': MethodType.POST,
    'users_acquire_lock': MethodType.PATCH,
    'users_release_lock': MethodType.PATCH,
    'admins': MethodType.POST,
    'superuser': MethodType.POST,
    'token': MethodType.POST,
}


@pytest.mark.parametrize(
    'url, method_type, status_code',
    [
        (
            '/users',
            URLS_METHOD_TYPES['users'],
            HTTPStatus.UNAUTHORIZED,
        ),
        (
            '/users',
            URLS_METHOD_TYPES['users_post'],
            HTTPStatus.UNAUTHORIZED,
        ),
        (
            '/users/1/acquire_lock',
            URLS_METHOD_TYPES['users_acquire_lock'],
            HTTPStatus.UNAUTHORIZED,
        ),
        (
            '/users/1/release_lock',
            URLS_METHOD_TYPES['users_release_lock'],
            HTTPStatus.UNAUTHORIZED,
        ),
        (
            '/admins',
            URLS_METHOD_TYPES['admins'],
            HTTPStatus.UNAUTHORIZED,
        ),
        (
            '/superuser',
            URLS_METHOD_TYPES['superuser'],
            HTTPStatus.CREATED,
        ),
    ],
)
@pytest.mark.asyncio
async def test_routes_availability_without_token(
    async_client: AsyncClient,
    async_session: AsyncSession,
    create_user: None,
    url: str,
    method_type: MethodType,
    status_code: int,
):
    if method_type == MethodType.GET:
        response = await async_client.get(url)
    elif method_type == MethodType.POST:
        response = await async_client.post(url)
    elif method_type == MethodType.PUT:
        response = await async_client.put(url)
    elif method_type == MethodType.PATCH:
        response = await async_client.patch(url)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    'url, method_type, status_code',
    [
        (
            '/users',
            URLS_METHOD_TYPES['users'],
            HTTPStatus.OK,
        ),
        (
            '/users',
            URLS_METHOD_TYPES['users_post'],
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            '/users/1/acquire_lock',
            URLS_METHOD_TYPES['users_acquire_lock'],
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            '/users/1/release_lock',
            URLS_METHOD_TYPES['users_release_lock'],
            HTTPStatus.OK,
        ),
        (
            '/admins',
            URLS_METHOD_TYPES['admins'],
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
    ],
)
@pytest.mark.asyncio
async def test_routes_availability_with_token(
    async_client: AsyncClient,
    async_session: AsyncSession,
    create_user: None,
    url: str,
    method_type: MethodType,
    status_code: int,
    token: str,
):
    if method_type == MethodType.GET:
        response = await async_client.get(
            url,
            headers={'Authorization': 'Bearer ' + token},
        )
    elif method_type == MethodType.POST:
        response = await async_client.post(
            url,
            headers={'Authorization': 'Bearer ' + token},
        )
    elif method_type == MethodType.PUT:
        response = await async_client.put(
            url,
            headers={'Authorization': 'Bearer ' + token},
        )
    elif method_type == MethodType.PATCH:
        response = await async_client.patch(
            url,
            headers={'Authorization': 'Bearer ' + token},
        )
    assert response.status_code == status_code


@pytest.mark.asyncio
async def test_token_availability(
    async_client: AsyncClient,
    async_session: AsyncSession,
):
    await async_client.post('/superuser')
    data = {'username': ADMIN0_LOGIN, 'password': ADMIN0_PASSWORD}
    response_token = await async_client.post('/token', data=data)
    assert response_token.status_code == HTTPStatus.CREATED
