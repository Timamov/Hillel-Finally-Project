import json
from enum import Enum
from typing import Annotated

from fastapi import FastAPI, Query, status
from fastapi import FastAPI, Query, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field



oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/token')


app = FastAPI(
    description='First site'
)
def index():
    return {'status': 200}


fake_db_users = [
    {
        'username': 'alex',
        'password': 'admin',
        'is_admin': True,
        'token': 'eb038beaac3f45de8831b9a584da1218',
    },
    {
        'username': 'alice',
        'password': 'secret',
        'is_admin': False,
        'token': 'eb038beafc3f45de8831b9a584da1210',
    },
]


class User(BaseModel):
    username: str
    is_admin: bool
    token: str
    password: str


@app.post('/api/token')
def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    user_dict = {}
    for user in fake_db_users:
        found_user = user['username'] == form_data.username
        if found_user:
            user_dict = user
            break
    if not user_dict:
        raise HTTPException(status_code=400, detail='Incorrect username or password')

    user = User(**user_dict)
    password = form_data.password
    if password != user.password:
        raise HTTPException(status_code=400, detail='Incorrect username or password')

    return {'access_token': user.token, 'token_type': 'bearer'}


def get_user_by_token(token: str, is_admin: bool = False) -> User:
    user = None
    for user_data in fake_db_users:
        if token == user_data['token']:
            if is_admin:
                if not user_data['is_admin']:
                    raise HTTPException(status_code=403, detail='You do not have enough permissions')
            user = User(**user_data)
            break
    if not user:
        raise HTTPException(status_code=403, detail='Invalid credentials')

    return user


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User | None:
    user = get_user_by_token(token)
    return user


def get_current_user_admin(token: Annotated[str, Depends(oauth2_scheme)]) -> User | None:
    user = get_user_by_token(token, is_admin=True)
    return user
