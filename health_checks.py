from http import HTTPStatus

from fastapi import FastAPI
from fastapi_healthchecks.checks import Check, CheckResult
from httpx import ASGITransport, AsyncClient


class AmIAlive(Check):
    async def __call__(self) -> CheckResult:
        return CheckResult(name='I\'m alive!', passed=True)


class IsSuperuserEndpointAlive(Check):
    def __init__(self, app: FastAPI) -> None:
        self._app = app

    async def __call__(self) -> CheckResult:
        async with AsyncClient(
            transport=ASGITransport(app=self._app),
            base_url='http://test',
        ) as client:
            response = await client.post('/superuser')
            if response.status_code == HTTPStatus.CREATED:
                return CheckResult(name='/superuser availability', passed=True)
            return CheckResult(
                name='/superuser availability',
                passed=False,
                details=f'/superuser is not available.'
                f'Error code: {response.status_code}.'
                f'Detail: {response.json()}',
            )
