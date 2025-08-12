from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List
from src.entities.action_status import ActionStatus
from src.entities.user_change_log import UserChangeLog
from src.entities.user import User
from . import models

ACTION_NOT_FOUND = "Action not found"


def get_or_create_action(db: Session, name: str, description: str = "") -> ActionStatus:
    action = db.query(ActionStatus).filter(ActionStatus.name == name).first()
    if action:
        return action
    action = ActionStatus(name=name, description=description)
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


def create_action(db: Session, action_in: models.ActionStatusCreate) -> ActionStatus:
    existing = db.query(ActionStatus).filter(ActionStatus.name == action_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Action already exists")
    action = ActionStatus(name=action_in.name, description=action_in.description)
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


def list_actions(db: Session) -> List[ActionStatus]:
    return db.query(ActionStatus).all()


def log_user_change(db: Session, user_id: int, changed_by: int, action_name: str, field: str, old_value: str | None, new_value: str | None) -> UserChangeLog:
    for uid in (user_id, changed_by):
        if not db.query(User).filter(User.id == uid).first():
            raise HTTPException(status_code=404, detail=f"User {uid} not found")
    action = get_or_create_action(db, action_name, description=action_name)
    log = UserChangeLog(
        user_id=user_id,
        changed_by=changed_by,
        action_id=action.id,
        field_changed=field,
        old_value=old_value,
        new_value=new_value,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def list_user_logs(db: Session, user_id: int) -> List[UserChangeLog]:
    return db.query(UserChangeLog).filter(UserChangeLog.user_id == user_id).order_by(UserChangeLog.changed_at.desc()).all()


def list_all_logs(db: Session) -> List[UserChangeLog]:
    return db.query(UserChangeLog).order_by(UserChangeLog.changed_at.desc()).all()


def to_response(log: UserChangeLog, action_lookup: dict[int, str]) -> models.UserChangeLogResponse:
    return models.UserChangeLogResponse(
        id=log.id,
        user_id=log.user_id,
        changed_by=log.changed_by,
        action_id=log.action_id,
        action_name=action_lookup.get(log.action_id),
        field_changed=log.field_changed,
        old_value=log.old_value,
        new_value=log.new_value,
        changed_at=str(log.changed_at)
    )


def enrich_with_actions(db: Session, logs: List[UserChangeLog]) -> List[models.UserChangeLogResponse]:
    action_ids = {l.action_id for l in logs}
    actions = db.query(ActionStatus).filter(ActionStatus.id.in_(action_ids)).all() if action_ids else []
    lookup = {a.id: a.name for a in actions}
    return [to_response(l, lookup) for l in logs]
