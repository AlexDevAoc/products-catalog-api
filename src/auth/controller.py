from typing import Annotated
from fastapi import APIRouter, Depends
from starlette import status
from . import  models
from . import service
from fastapi.security import OAuth2PasswordRequestForm
from ..database.core import DbSession
from sqlalchemy.orm import Session

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_user(db: DbSession,
                      register_user_request: models.RegisterUserRequest):
    service.register_user(db, register_user_request)


@router.post("/token", response_model=models.Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: DbSession):
    return service.login_for_access_token(form_data, db)


@router.post("/anonymous/token", response_model=models.Token)
async def anonymous_access_token(db: DbSession):
    return service.anonymous_access_token(db)







