from fastapi import Depends, FastAPI
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from sql_app import crud, models, schemas
from sql_app.database import AsyncSession, async_session, engine, init_db

app = FastAPI()


# change this garbage to alembic
@app.on_event("startup")
async def on_startup():
    await init_db()


async def get_session():
    '''Dependency session.'''
    async with async_session() as session:
        yield session


# DELETE THIS LATER
@app.get("/")
async def root():
    return {"message": "Hello world!"}


@app.get("/users", response_model=list[schemas.User])
async def get_user(session: AsyncSession = Depends(get_session)) -> list[schemas.User]:
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


@app.post("/users")
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
