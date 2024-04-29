import os
from datetime import timedelta
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from api_security import jwt_passwords
from sql_app import crud, schemas
from sql_app.database import AsyncSession, get_session

app = FastAPI()


@app.get(
    '/users',
    response_model=list[schemas.User],
    dependencies=[Depends(jwt_passwords.check_jwt_token)],
)
async def get_user(
    # token: None = Depends(api_security.check_jwt_token),
    session: AsyncSession = Depends(get_session),
) -> list[schemas.User]:
    '''
    GET method users/ enpoint handler.

    Returns a list of user data.
    '''
    users = await crud.get_users(session)
    return [
        schemas.User(
            id=u.id,
            login=u.login,
            locktime=u.locktime,
            created_at=u.created_at,
            env=u.env,
            domain=u.domain,
            project_id=u.project_id,
            password=u.password,
        )
        for u in users
    ]


@app.post(
    '/users',
    response_model=schemas.User,
    status_code=HTTPStatus.CREATED,
    dependencies=[Depends(jwt_passwords.check_jwt_token)],
)
async def create_user(
    user: schemas.UserCreate, session: AsyncSession = Depends(get_session)
) -> schemas.User:
    '''
    POST method users/ enpoint handler.
    Expects a valid JSON data for sql_app.schemas.UserCreate Pydantic model.

    Returns created user's data.
    '''
    try:
        user = await crud.create_user(
            session=session,
            user=user,
        )
    except crud.IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f'user with login: {user.login} already exists',
        )
    return user


@app.patch(
    '/users/{id}/acquire_lock',
    response_model=schemas.User,
    dependencies=[Depends(jwt_passwords.check_jwt_token)],
)
async def acquire_lock(
    locktime: schemas.UserLockTime,
    id: int,
    session: AsyncSession = Depends(get_session),
) -> schemas.User:
    '''
    PATCH method users/{id: int}/acquire_lock enpoint handler.
    Expects a datetime value for the locktime field and sets that locktime.

    Returns modified user's data.
    '''
    try:
        user = await crud.acquire_release_lock(
            session=session,
            locktime=locktime.locktime,
            id=id,
        )
    except crud.NoResultFound:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='user not found'
        )
    except ValueError:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f'user with id: {id} is already occupied',
        )
    return user


@app.patch(
    '/users/{id}/release_lock',
    dependencies=[Depends(jwt_passwords.check_jwt_token)],
)
async def release_lock(
    id: int, session: AsyncSession = Depends(get_session)
) -> schemas.User:
    '''
    PATCH method users/{id: int}/release_lock enpoint handler.
    NUlls the locktime for the user.

    Returns modified user's data.
    '''
    user = await crud.acquire_release_lock(
        session=session,
        locktime=None,
        id=id,
    )
    return user


@app.post(
    '/admins',
    status_code=HTTPStatus.CREATED,
    dependencies=[Depends(jwt_passwords.check_jwt_token)],
)
async def create_admin(
    admin: schemas.AdminUser, session: AsyncSession = Depends(get_session)
) -> schemas.AdminUser:
    '''
    POST method admin/ enpoint handler.
    Expects a valid JSON data for sql_app.schemas.AdminUser Pydantic model.

    Returns created admin's data.
    '''
    try:
        admin = await crud.create_admin(
            session=session,
            admin=admin,
        )
    except crud.IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f'admin with login: {admin.login} already exists',
        )
    return admin


# костыль?
@app.post('/superuser', status_code=HTTPStatus.CREATED)
async def create_first_admin(
    session: AsyncSession = Depends(get_session),
) -> schemas.AdminUser:
    '''
    POST method superuser/ endpoint handler.
    Used for creating a base admin.
    '''
    db_admin0 = await crud.create_first_admin(
        session=session,
        login=os.getenv('ADMIN0LOGIN'),
        password=os.getenv('ADMIN0PASSWORD'),
    )
    return db_admin0


@app.post('/token')
async def get_token(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
) -> schemas.Token:
    '''
    POST method token/ endpoint handler.
    Expects login and password.

    Returns a JWT-token if presented credentials are correct.
    '''
    admin = await jwt_passwords.auth_admin(
        session=session,
        username=credentials.username,
        password=credentials.password,
    )
    if not admin:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=f'incorrect username or password',
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = jwt_passwords.create_access_token(
        data={'sub': admin.login},
        expires_delta=timedelta(
            minutes=jwt_passwords.ACCESS_TOKEN_EXPIRES_MINS
        ),
    )
    return schemas.Token(access_token=access_token, token_type='bearer')
