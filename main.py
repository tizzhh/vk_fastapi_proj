from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from sql_app import crud, models, schemas
from sql_app.database import AsyncSession, async_session, engine, init_db

app = FastAPI()


# models.Base.metadata.create_all(bind=engine, echo=True)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# alembic
@app.on_event("startup")
async def on_startup():
    await init_db()


async def get_session():
    async with async_session() as session:
        yield session


@app.get("/")
async def root():
    return {"message": "Hello world!"}


@app.get("/users", response_model=list[schemas.User])
async def get_user(session: AsyncSession = Depends(get_session)):
    users = await crud.get_users(session)
    return [schemas.User(**u) for u in users]
