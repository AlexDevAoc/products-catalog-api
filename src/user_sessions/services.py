from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone
from src.entities.user_session import UserSession


def create_session(db: Session, user_id: int, is_anonymous: bool = False) -> UserSession:
    # Optional policy: close existing open sessions for same user
    open_sessions = db.query(UserSession).filter(UserSession.user_id == user_id, UserSession.logout_at == None).all()
    for s in open_sessions:
        s.logout_at = datetime.now(timezone.utc)
    session = UserSession(user_id=user_id, is_anonymous=is_anonymous)
    db.add(session)
    db.commit(); db.refresh(session)
    return session


def close_session(db: Session, session_id: int, user_id: int) -> UserSession:
    session = db.query(UserSession).filter(UserSession.id == session_id, UserSession.user_id == user_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.logout_at is None:
        session.logout_at = datetime.now(timezone.utc)
        db.commit(); db.refresh(session)
    return session


def list_user_sessions(db: Session, user_id: int):
    return db.query(UserSession).filter(UserSession.user_id == user_id).order_by(UserSession.login_at.desc()).all()


def get_active_session(db: Session, user_id: int):
    return db.query(UserSession).filter(UserSession.user_id == user_id, UserSession.logout_at == None).order_by(UserSession.login_at.desc()).first()
