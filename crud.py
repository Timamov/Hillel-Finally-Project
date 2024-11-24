
import json
from enum import Enum
from typing import Annotated

from fastapi import FastAPI, Query, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from storage import storage

app = FastAPI(
    description='Tour agency'
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/token')

class TourTypes(str, Enum):
    OCITY = 'only cities'
    NATWITHCITY = 'cities and nature'
    ONATURE = 'only nature'
    MOUNTCLMB = 'climbing on mountains(camping)'
    MOUNTRESORTWITHCLMB = 'climbing on mountains and living in resort'


class NewTour(BaseModel):
    title: str = Field(min_length=10,
                       examples=['Intence hot tour to', 'Big tour throw popular cities', 'Almost sold out!'])
    country: str
    date: str
    duration: str
    price: float = Field(default=700, gt=0.0)
    tags: list[TourTypes] = Field(default=[])
    description: str


class SavedTour(NewTour):
    id: str = Field(examples=['b3b2d5d99c1b4d1e99fdce05ae3b5988'])


@app.get('/')
def test():
    return {'detail': 'succesfully works'}



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

@app.post('/api/create', status_code=status.HTTP_201_CREATED)
def create_tour(tour: NewTour, admin_user: Annotated[User, Depends(get_current_user_admin)]) -> SavedTour:
    created_tour = storage.create_tour(json.loads(tour.json()))
    return created_tour


@app.get('/api/get-tours/')
def get_tours(any_user: Annotated[User, Depends(get_current_user)], skip: int = Query(default=0, ge=0), limit: int = Query(default=10, gt=0), search: str = '' ) -> list[SavedTour]:
    saved_tours = storage.get_tours(skip, limit, search)
    return saved_tours


@app.get('/api/get-tours/{tour_id}')
def get_info_tour(tour_id: str, any_user: Annotated[User, Depends(get_current_user)]) -> SavedTour:
    saved_tour = storage.get_info_tour(tour_id)
    return saved_tour


@app.delete('/api/get-tours/{tour_id}')
def delete_tour(tour_id: str, admin_user: Annotated[User, Depends(get_current_user_admin)]) -> dict:
    storage.delete_tour(tour_id)
    return {}


@app.patch('/api/get-tours/{tour_id}')
def update_tour(tour_id: str, title: str, admin_user: Annotated[User, Depends(get_current_user_admin)]):
    tour = storage.update_tour(tour_id, title=title)
    return tour


if __name__ == "__main__":
    import uvicorn

    uvicorn.run('crud:app', reload=True, host='127.0.0.1', port=12000)


