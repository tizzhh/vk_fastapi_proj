import os
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Annotated, Union

import bcrypt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from sql_app import crud, schemas
from sql_app.database import AsyncSession, get_session

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRES_MINS = 60
DEFAULT_EXPIRE_TIME = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def check_jwt_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session),
):
    '''Function checks whether or not the token is valid.'''
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    admin = await crud.get_user_admin(
        session=session, type=crud.QueryTypes.ADMIN, login=username
    )
    if admin is None:
        raise credentials_exception
    return admin


async def auth_admin(
    session: AsyncSession, username: str, password: str
) -> schemas.AdminUser:
    '''Function that checks whether or not a user is an admin based on presented login and password.'''
    admin = await crud.get_user_admin(
        session=session,
        type=crud.QueryTypes.ADMIN,
        login=username,
    )
    if admin is None:
        return False
    if not verify_password(password, admin.password):
        return False
    return admin


def verify_password(password: str, hashed_pass: bytes) -> bool:
    '''Function that verifies password.'''
    return bcrypt.checkpw(password.encode('utf-8'), hashed_pass)


def create_access_token(
    data: dict, expires_delta: Union[timedelta, None]
) -> str:
    '''Function that creates a JWT-token.'''
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=DEFAULT_EXPIRE_TIME
        )
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
