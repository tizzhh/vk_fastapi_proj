from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException

from sql_app import crud, schemas
from sql_app.database import AsyncSession, async_session

app = FastAPI()


async def get_session():
    '''Dependency session.'''
    async with async_session() as session:
        yield session


@app.get("/users", response_model=list[schemas.User])
async def get_user(
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
        )
        for u in users
    ]


@app.post(
    "/users", response_model=schemas.User, status_code=HTTPStatus.CREATED
)
async def create_user(
    user: schemas.UserCreate, session: AsyncSession = Depends(get_session)
) -> schemas.User:
    '''
    POST method users/ enpoint handler.
    Expects a valid JSON data for sql_app.schemas.UserCreate Pydantic model.

    Returns created user's data.
    '''
    user = await crud.create_user(session, user)
    return user


@app.patch("/users/{id}/acquire_lock", response_model=schemas.User)
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
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='user not found'
        )
    except ValueError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f'user with id: {id} is already occupied',
        )
    return user


@app.patch("/users/{id}/release_lock")
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
