from fastapi import APIRouter, status
from typing import List
from ..database.core import DbSession
from ..auth.service import CurrentUser
from . import services as service
from . import models

router = APIRouter(
    prefix="/user-change-logs",
    tags=["UserChangeLogs"]
)


@router.get("/", response_model=List[models.UserChangeLogResponse])
def list_logs(db: DbSession):
    logs = service.list_all_logs(db)
    return service.enrich_with_actions(db, logs)


@router.get("/user/{user_id}", response_model=List[models.UserChangeLogResponse])
def list_user_logs(user_id: int, db: DbSession):
    logs = service.list_user_logs(db, user_id)
    return service.enrich_with_actions(db, logs)


@router.get("/me", response_model=List[models.UserChangeLogResponse])
def my_logs(current_user: CurrentUser, db: DbSession):
    logs = service.list_user_logs(db, current_user.user_id)
    return service.enrich_with_actions(db, logs)


@router.get("/actions", response_model=List[models.ActionStatusResponse])
def list_actions(db: DbSession):
    return service.list_actions(db)


@router.post("/actions", response_model=models.ActionStatusResponse, status_code=status.HTTP_201_CREATED)
def create_action(action_in: models.ActionStatusCreate, db: DbSession):
    return service.create_action(db, action_in)
