from fastapi import APIRouter
from typing import List
from ..database.core import DbSession
from ..auth.service import CurrentUser
from . import services as service
from . import models

router = APIRouter(
    prefix="/sessions",
    tags=["UserSessions"]
)


@router.get("/me", response_model=List[models.UserSessionResponse])
def my_sessions(current_user: CurrentUser, db: DbSession):
    sessions = service.list_user_sessions(db, current_user.user_id)
    return sessions


@router.get("/me/active", response_model=models.UserActiveSessionResponse)
def my_active_session(current_user: CurrentUser, db: DbSession):
    active = service.get_active_session(db, current_user.user_id)
    return models.UserActiveSessionResponse(has_active=active is not None, session_id=active.id if active else None)


@router.post("/me/{session_id}/close", response_model=models.UserSessionCloseResponse)
def close_my_session(session_id: int, current_user: CurrentUser, db: DbSession):
    session = service.close_session(db, session_id, current_user.user_id)
    return models.UserSessionCloseResponse(id=session.id, logout_at=str(session.logout_at))
