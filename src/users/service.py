from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models
from src.entities.user import User
from src.exceptions import UserNotFoundError, InvalidPasswordError, PasswordMismatchError
from src.auth.service import verify_password, get_password_hash, CurrentUser
from src.user_change_logs import services as change_log_service
import logging

def get_users(db: Session) -> list[models.UserResponse]:
    users = db.query(User).all()
    logging.info(f"Successfully retrieved {len(users)} users.")
    return users

def get_user_by_id(db: Session, user_id: int) -> models.UserResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logging.warning(f"User not found with ID: {user_id}")
        raise UserNotFoundError(user_id)
    logging.info(f"Successfully retrieved user with ID: {user_id}")
    return user


def change_password(db: Session, user_id: int, password_change: models.PasswordChange) -> None:
    try:
        user = get_user_by_id(db, user_id)
        
        if not verify_password(password_change.current_password, user.password):
            logging.warning(f"Invalid current password provided for user ID: {user_id}")
            raise InvalidPasswordError()
        
        if password_change.new_password != password_change.new_password_confirm:
            logging.warning(f"Password mismatch during change attempt for user ID: {user_id}")
            raise PasswordMismatchError()
        
        user.password = get_password_hash(password_change.new_password)
        db.commit()
        try:
            change_log_service.log_user_change(
                db=db,
                user_id=user_id,
                changed_by=user_id,
                action_name="PASSWORD_CHANGE",
                field="password",
                old_value="***",
                new_value="***"
            )
        except Exception as le:
            logging.error(f"Failed to log password change for user {user_id}: {le}")
        logging.info(f"Successfully changed password for user ID: {user_id}")
    except Exception as e:
        logging.error(f"Error during password change for user ID: {user_id}. Error: {str(e)}")
        raise


def update_user(db: Session, target_user_id: int, update_in: models.UserUpdate, admin_user: CurrentUser) -> User:
    user = db.query(User).filter(User.id == target_user_id).first()
    if not user:
        raise UserNotFoundError(target_user_id)

    def snapshot(u: User):
        return {
            "first_name": u.first_name,
            "last_name": u.last_name,
            "email": u.email,
            "status": u.status,
        }

    before = snapshot(user)

    # Apply mutations
    mutations = {
        "first_name": update_in.first_name,
        "last_name": update_in.last_name,
        "status": update_in.status,
    }
    for field, value in mutations.items():
        if value is not None:
            setattr(user, field, value)

    _update_user_email(db, user, update_in)

    db.commit()
    db.refresh(user)
    after = snapshot(user)

    _log_user_changes(db, target_user_id, admin_user.user_id, before, after)

    return user

def _update_user_email(db: Session, user: User, update_in: models.UserUpdate) -> None:
    if update_in.email is not None and update_in.email != user.email:
        exists = db.query(User).filter(User.email == update_in.email, User.id != user.id).first()
        if exists:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = update_in.email

def _log_user_changes(db: Session, target_user_id: int, changed_by: int, before: dict, after: dict) -> None:
    for field, old_val in before.items():
        new_val = after[field]
        if old_val == new_val:
            continue
        try:
            change_log_service.log_user_change(
                db=db,
                user_id=target_user_id,
                changed_by=changed_by,
                action_name="UPDATE_USER",
                field=field,
                old_value=str(old_val) if old_val is not None else None,
                new_value=str(new_val) if new_val is not None else None,
            )
        except Exception as le:
            logging.error(f"Failed to log user update for user {target_user_id}: {le}")


def soft_delete_user(db: Session, target_user_id: int, admin_user: CurrentUser) -> None:
    user = db.query(User).filter(User.id == target_user_id).first()
    if not user:
        raise UserNotFoundError(target_user_id)
    if not user.status:
        return
    old_status = user.status
    user.status = False
    db.commit()
    try:
        change_log_service.log_user_change(
            db=db,
            user_id=target_user_id,
            changed_by=admin_user.user_id,
            action_name="DELETE_USER",
            field="status",
            old_value=str(old_status),
            new_value=str(user.status),
        )
    except Exception as le:
        logging.error(f"Failed to log user soft delete for user {target_user_id}: {le}")
