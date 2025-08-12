from fastapi import APIRouter, status
from typing import List

from ..database.core import DbSession
from . import models
from . import services as service
from ..auth.service import CurrentUser

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"]
)


@router.get("/", response_model=List[models.PermissionResponse])
def list_permissions(db: DbSession):
    return service.list_permissions(db)


@router.get("/{permission_id}", response_model=models.PermissionResponse)
def get_permission(permission_id: int, db: DbSession):
    return service.get_permission(db, permission_id)


@router.post("/", response_model=models.PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(perm_in: models.PermissionCreate, db: DbSession):
    return service.create_permission(db, perm_in)


@router.put("/{permission_id}", response_model=models.PermissionResponse)
def update_permission(permission_id: int, perm_in: models.PermissionUpdate, db: DbSession):
    return service.update_permission(db, permission_id, perm_in)


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_permission(permission_id: int, db: DbSession):
    service.soft_delete_permission(db, permission_id)


@router.post("/assign", status_code=status.HTTP_204_NO_CONTENT)
def assign_permission(payload: models.AssignPermissionRequest, db: DbSession):
    service.assign_permission_to_role(db, payload.role_id, payload.permission_id)


@router.get("/role/{role_id}", response_model=models.RolePermissionsResponse)
def role_permissions(role_id: int, db: DbSession):
    perms = service.list_role_permissions(db, role_id)
    return models.RolePermissionsResponse(role_id=role_id, permissions=perms)


@router.get("/user/{user_id}", response_model=models.UserPermissionsResponse)
def user_permissions(user_id: int, db: DbSession):
    perms = service.list_user_permissions(db, user_id)
    return models.UserPermissionsResponse(user_id=user_id, permissions=perms)


@router.get("/current/user", response_model=models.UserPermissionsResponse)
def current_user_permissions(current_user: CurrentUser, db: DbSession):
    perms = service.list_user_permissions(db, current_user.user_id)
    return models.UserPermissionsResponse(user_id=current_user.user_id, permissions=perms)
