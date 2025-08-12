from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List

from src.entities.permission import Permission
from src.entities.role import Role
from src.entities.role_permission import RolePermission
from src.entities.user_role import UserRole
from src.entities.user import User
from . import models

PERMISSION_NOT_FOUND = "Permission not found"


def list_permissions(db: Session) -> List[Permission]:
    return db.query(Permission).all()


def get_permission(db: Session, permission_id: int) -> Permission:
    perm = db.query(Permission).filter(Permission.id == permission_id).first()
    if not perm:
        raise HTTPException(status_code=404, detail=PERMISSION_NOT_FOUND)
    return perm


def create_permission(db: Session, perm_in: models.PermissionCreate) -> Permission:
    existing = db.query(Permission).filter(Permission.name == perm_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Permission name already exists")
    perm = Permission(name=perm_in.name, description=perm_in.description, status=perm_in.status)
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm


def update_permission(db: Session, permission_id: int, perm_in: models.PermissionUpdate) -> Permission:
    perm = get_permission(db, permission_id)
    if perm_in.name is not None and perm_in.name != perm.name:
        exists = db.query(Permission).filter(Permission.name == perm_in.name).first()
        if exists:
            raise HTTPException(status_code=400, detail="Permission name already exists")
        perm.name = perm_in.name
    if perm_in.description is not None:
        perm.description = perm_in.description
    if perm_in.status is not None:
        perm.status = perm_in.status
    db.commit()
    db.refresh(perm)
    return perm


def soft_delete_permission(db: Session, permission_id: int) -> None:
    perm = get_permission(db, permission_id)
    perm.status = False
    db.commit()


def assign_permission_to_role(db: Session, role_id: int, permission_id: int) -> None:
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    perm = db.query(Permission).filter(Permission.id == permission_id).first()
    if not perm:
        raise HTTPException(status_code=404, detail=PERMISSION_NOT_FOUND)
    exists = db.query(RolePermission).filter(RolePermission.role_id == role_id, RolePermission.permission_id == permission_id).first()
    if exists:
        return  # idempotente
    db.add(RolePermission(role_id=role_id, permission_id=permission_id))
    db.commit()


def list_role_permissions(db: Session, role_id: int) -> List[Permission]:
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    perms = (
        db.query(Permission)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .filter(RolePermission.role_id == role_id)
        .all()
    )
    return perms


def list_user_permissions(db: Session, user_id: int) -> List[Permission]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_role = db.query(UserRole).filter(UserRole.user_id == user_id).first()
    if not user_role:
        return []
    return list_role_permissions(db, user_role.role_id)
