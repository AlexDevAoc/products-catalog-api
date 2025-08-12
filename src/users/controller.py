from fastapi import APIRouter, status, Depends

from ..database.core import DbSession
from . import models
from . import service
from ..auth.service import CurrentUser
from ..roles.services import require_admin

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/", response_model=list[models.UserResponse], dependencies=[Depends(require_admin)])
def get_all_users(db: DbSession):
    return service.get_users(db)

@router.get("/me", response_model=models.UserResponse)
def get_current_user(current_user: CurrentUser, db: DbSession):
    return service.get_user_by_id(db, current_user.user_id)


@router.put("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    password_change: models.PasswordChange,
    db: DbSession,
    current_user: CurrentUser
):
    service.change_password(db, current_user.user_id, password_change)


@router.put("/{user_id}", response_model=models.UserResponse, dependencies=[Depends(require_admin)])
def update_user(user_id: int, update_in: models.UserUpdate, db: DbSession, current_user: CurrentUser):
    return service.update_user(db, user_id, update_in, admin_user=current_user)


@router.delete("/{user_id}", status_code=204, dependencies=[Depends(require_admin)])
def soft_delete_user(user_id: int, db: DbSession, current_user: CurrentUser):
    service.soft_delete_user(db, user_id, admin_user=current_user)
    return None
