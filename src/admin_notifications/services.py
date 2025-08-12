from sqlalchemy.orm import Session
from typing import List

from src.entities.admin_notification import AdminNotification
from src.entities.notification_status import NotificationStatus
from src.entities.user import User
from . import models


def list_notifications(db: Session) -> List[AdminNotification]:
    return db.query(AdminNotification).order_by(AdminNotification.sent_at.desc()).all()


def list_notifications_by_user(db: Session, user_id: int) -> List[AdminNotification]:
    return db.query(AdminNotification).filter(AdminNotification.sent_to == user_id).order_by(AdminNotification.sent_at.desc()).all()

def to_response(db: Session, notif: AdminNotification) -> models.AdminNotificationResponse:
    status = db.query(NotificationStatus).filter(NotificationStatus.id == notif.status_id).first()
    user = db.query(User).filter(User.id == notif.sent_to).first()
    return models.AdminNotificationResponse(
        id=notif.id,
        change_log_id=notif.change_log_id,
        sent_to=notif.sent_to,
        sent_to_email=user.email if user else None,
        status=status.name if status else "UNKNOWN",
        message=notif.message,
        error_message=notif.error_message,
        sent_at=str(notif.sent_at)
    )


def enrich(db: Session, notifs: List[AdminNotification]) -> List[models.AdminNotificationResponse]:
    status_ids = {n.status_id for n in notifs}
    statuses = db.query(NotificationStatus).filter(NotificationStatus.id.in_(status_ids)).all() if status_ids else []
    status_lookup = {s.id: s.name for s in statuses}
    user_ids = {n.sent_to for n in notifs}
    users = db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
    user_lookup = {u.id: u.email for u in users}
    return [models.AdminNotificationResponse(
        id=n.id,
        change_log_id=n.change_log_id,
        sent_to=n.sent_to,
        sent_to_email=user_lookup.get(n.sent_to),
        status=status_lookup.get(n.status_id, "UNKNOWN"),
        message=n.message,
        error_message=n.error_message,
        sent_at=str(n.sent_at)
    ) for n in notifs]
