from sqlalchemy.orm import Session
from fastapi import HTTPException, Request, Depends
from typing import List
from src.auth.service import CurrentUser
from src.database.core import get_db

from src.entities.role import Role
from src.entities.user import User
from src.entities.user_role import UserRole
from . import models

ROLE_NOT_FOUND = "Role not found"


def list_roles(db: Session) -> List[Role]:
    return db.query(Role).all()


def get_role(db: Session, role_id: int) -> Role:
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail=ROLE_NOT_FOUND)
    return role


def create_role(db: Session, role_in: models.RoleCreate) -> Role:
    existing = db.query(Role).filter(Role.name == role_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role name already exists")
    role = Role(name=role_in.name, description=role_in.description, status=role_in.status)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def update_role(db: Session, role_id: int, role_in: models.RoleUpdate) -> Role:
    role = get_role(db, role_id)
    if role_in.name is not None:
        if role_in.name != role.name:
            exists = db.query(Role).filter(Role.name == role_in.name).first()
            if exists:
                raise HTTPException(status_code=400, detail="Role name already exists")
        role.name = role_in.name
    if role_in.description is not None:
        role.description = role_in.description
    if role_in.status is not None:
        role.status = role_in.status
    db.commit()
    db.refresh(role)
    return role


def soft_delete_role(db: Session, role_id: int) -> None:
    role = get_role(db, role_id)
    role.status = False
    db.commit()


def get_user_role(db: Session, user_id: int) -> Role:
    user_role =  db.query(UserRole).filter(UserRole.user_id == user_id).first()
    if not user_role:
        raise HTTPException(status_code=404, detail="User has no role assigned")
    role =  db.query(Role).filter(Role.id == user_role.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail=ROLE_NOT_FOUND)
    return role


def assign_role(db: Session, user_id: int, role_id: int) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail=ROLE_NOT_FOUND)
    existing = db.query(UserRole).filter(UserRole.user_id == user_id).first()
    if existing:
        existing.role_id = role_id
    else:
        db.add(UserRole(user_id=user_id, role_id=role_id))
    db.commit()


# --- Role-based access helper dependencies ---

ADMIN_ROLE = "admin"
ANONYMOUS_ROLE = "anonymous"


def get_current_user_role(db: Session, current_user: CurrentUser) -> Role:
    return get_user_role(db, current_user.user_id)


def require_role(required: str):
    def dependency(current_user: CurrentUser, db: Session = Depends(get_db)):
        role = get_user_role(db, current_user.user_id)
        if role.name != required:
            raise HTTPException(status_code=403, detail=f"{required} role required")
        return role
    return dependency


def require_admin(current_user: CurrentUser, db: Session = Depends(get_db)):
    role = get_user_role(db, current_user.user_id)
    if role.name != ADMIN_ROLE:
        raise HTTPException(status_code=403, detail="Admin role required")
    return role


def require_anonymous_or_admin_read_get(current_user: CurrentUser, request: Request, db: Session = Depends(get_db)):
    role = get_user_role(db, current_user.user_id)
    if _is_admin(role):
        return role
    if _is_anonymous(role) and request.method == "GET":
        return role
    _deny_access()


def _is_admin(role: Role) -> bool:
    return role.name == ADMIN_ROLE


def _is_anonymous(role: Role) -> bool:
    return role.name == ANONYMOUS_ROLE


def _deny_access():
    raise HTTPException(status_code=403, detail="Not enough permissions")

