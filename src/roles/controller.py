from fastapi import APIRouter, status
from typing import List

from ..database.core import DbSession
from . import models
from . import services as service
from ..auth.service import CurrentUser

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

@router.get("/", response_model=List[models.RoleResponse])
def list_roles(db: DbSession):
    return service.list_roles(db)


@router.get("/{role_id}", response_model=models.RoleResponse)
def get_role(role_id: int, db: DbSession):
    return service.get_role(db, role_id)


@router.post("/", response_model=models.RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(role_in: models.RoleCreate, db: DbSession):
    return service.create_role(db, role_in)


@router.put("/{role_id}", response_model=models.RoleResponse)
def update_role(role_id: int, role_in: models.RoleUpdate, db: DbSession):
    return service.update_role(db, role_id, role_in)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_role(role_id: int, db: DbSession):
    service.soft_delete_role(db, role_id)


@router.post("/assign", status_code=status.HTTP_204_NO_CONTENT)
def assign_role(payload: models.AssignRoleRequest, db: DbSession):
    service.assign_role(db, payload.user_id, payload.role_id)


@router.get("/current/user", response_model=models.RoleResponse)
def get_current_role(current_user: CurrentUser, db: DbSession):
    return service.get_user_role(db, current_user.user_id)
