"""Notification service using SendGrid.

High level flow:
    diff_and_log() -> send_admin_notifications_for_product_change([...logs])
        -> validate config & gather active admins
        -> build grouped message (all field changes)
        -> persist AdminNotification rows as PENDING
        -> attempt send (single email to all admins)
        -> update rows to SENT or ERROR

Environment variables:
    SENDGRID_API_KEY
    NOTIFICATION_SENDER
    ENABLE_EMAIL_NOTIFICATIONS=true|false
"""

import os
from typing import List, Sequence, Tuple
from sqlalchemy.orm import Session
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from src.entities.product_change_log import ProductChangeLog
from src.entities.user_change_log import UserChangeLog
from src.entities.admin_notification import AdminNotification
from src.entities.product import Product
from src.entities.notification_status import NotificationStatus
from src.entities.user import User
from src.entities.user_role import UserRole
from src.entities.role import Role
from src.roles.services import ADMIN_ROLE

logger = logging.getLogger(__name__)

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
NOTIFICATION_SENDER = os.getenv("NOTIFICATION_SENDER")  # verified sender / single-sender
ENABLE_EMAIL_NOTIFICATIONS = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "false").lower() == "true"

NOTIF_STATUS_PENDING = "PENDING"
NOTIF_STATUS_SENT = "SENT"
NOTIF_STATUS_ERROR = "ERROR"


def _get_or_create_status(db: Session, name: str) -> NotificationStatus:
    status = db.query(NotificationStatus).filter(NotificationStatus.name == name).first()
    if status:
        return status
    status = NotificationStatus(name=name, description=name)
    db.add(status); db.commit(); db.refresh(status)
    return status


def _sg_client():
    return SendGridAPIClient(SENDGRID_API_KEY)


def _active_admins(db: Session) -> List[User]:
    role = db.query(Role).filter(Role.name == ADMIN_ROLE).first()
    if not role:
        return []
    user_ids = [ur.user_id for ur in db.query(UserRole).filter(UserRole.role_id == role.id).all()]
    if not user_ids:
        return []
    return db.query(User).filter(User.id.in_(user_ids), User.status == True).all()  # noqa: E712


def _validate_config() -> bool:
    if not ENABLE_EMAIL_NOTIFICATIONS:
        logger.debug("Email notifications disabled by flag")
        return False
    missing = [name for name, val in {
        "SENDGRID_API_KEY": SENDGRID_API_KEY,
        "NOTIFICATION_SENDER": NOTIFICATION_SENDER,
    }.items() if not val]
    if missing:
        logger.warning("Skipping email send, missing config vars: %s", ", ".join(missing))
        return False
    return True


def _email_content(product: Product | None, changer: User | None, diffs: Sequence[ProductChangeLog]) -> Tuple[str, str]:
    if not diffs:
        return "", ""
    product_id = diffs[0].product_id
    name = product.name if product else f"#{product_id}"
    changer_email = changer.email if changer else f"user:{diffs[0].changed_by}"
    subject = (
        f"Product '{name}' (#{product_id}) field {diffs[0].field_changed} updated"
        if len(diffs) == 1 else
        f"Product '{name}' (#{product_id}) updated ({len(diffs)} changes)"
    )
    lines = [f"- {d.field_changed}: {d.old_value} -> {d.new_value}" for d in diffs]
    body = f"Product '{name}' (ID {product_id}) updated by {changer_email}.\n\nChanges:\n" + "\n".join(lines)
    return subject, body


def send_admin_notifications_for_product_change(db: Session, change_logs: List[ProductChangeLog]):
    if not (change_logs and _validate_config()):
        return
    product_id = change_logs[0].product_id
    changer_id = change_logs[0].changed_by
    admins = _active_admins(db)
    if not admins:
        logger.info("No active admin users to notify")
        return

    product = db.query(Product).filter(Product.id == product_id).first()
    changer = db.query(User).filter(User.id == changer_id).first()
    subject, body = _email_content(product, changer, change_logs)
    if not subject:
        return

    pending = _get_or_create_status(db, NOTIF_STATUS_PENDING)
    sent = _get_or_create_status(db, NOTIF_STATUS_SENT)
    error = _get_or_create_status(db, NOTIF_STATUS_ERROR)

    notifications = [
        AdminNotification(
            change_log_id=change_logs[-1].id,
            sent_to=u.id,
            status_id=pending.id,
            message=body,
        ) for u in admins
    ]
    db.add_all(notifications); db.commit()

    mail = Mail(
        from_email=NOTIFICATION_SENDER,
        to_emails=[u.email for u in admins],
        subject=subject,
        plain_text_content=body,
    )
    try:
        resp = _sg_client().send(mail)
        ok = 200 <= resp.status_code < 300
        target_status_id = sent.id if ok else error.id
        err_text = None if ok else f"SendGrid status {resp.status_code}: {resp.body}"
        if err_text:
            logger.error(err_text)
        for n in notifications:
            n.status_id = target_status_id
            if err_text:
                n.error_message = err_text
    except Exception as e: 
        err_text = str(e)
        logger.exception("SendGrid send failed: %s", err_text)
        for n in notifications:
            n.status_id = error.id
            n.error_message = err_text
    db.commit()


def _user_email_content(user: User | None, changer: User | None, diffs: Sequence[UserChangeLog]) -> Tuple[str, str]:
    if not diffs:
        return "", ""
    user_id = diffs[0].user_id
    user_email = user.email if user else f"#{user_id}"
    changer_email = changer.email if changer else f"user:{diffs[0].changed_by}"
    subject = (
        f"User '{user_email}' (#{user_id}) field {diffs[0].field_changed} updated"
        if len(diffs) == 1 else
        f"User '{user_email}' (#{user_id}) updated ({len(diffs)} changes)"
    )
    lines = [f"- {d.field_changed}: {d.old_value} -> {d.new_value}" for d in diffs]
    body = f"User '{user_email}' (ID {user_id}) updated by {changer_email}.\n\nChanges:\n" + "\n".join(lines)
    return subject, body


def send_admin_notifications_for_user_change(db: Session, change_logs: List[UserChangeLog]):
    if not (change_logs and _validate_config()):
        return
    user_id = change_logs[0].user_id
    changer_id = change_logs[0].changed_by
    admins = _active_admins(db)
    if not admins:
        logger.info("No active admin users to notify (user change)")
        return

    user = db.query(User).filter(User.id == user_id).first()
    changer = db.query(User).filter(User.id == changer_id).first()
    subject, body = _user_email_content(user, changer, change_logs)
    if not subject:
        return

    pending = _get_or_create_status(db, NOTIF_STATUS_PENDING)
    sent = _get_or_create_status(db, NOTIF_STATUS_SENT)
    error = _get_or_create_status(db, NOTIF_STATUS_ERROR)

    notifications = [
        AdminNotification(
            user_change_log_id=change_logs[-1].id,
            sent_to=u.id,
            status_id=pending.id,
            message=body,
        ) for u in admins
    ]
    db.add_all(notifications); db.commit()

    mail = Mail(
        from_email=NOTIFICATION_SENDER,
        to_emails=[u.email for u in admins],
        subject=subject,
        plain_text_content=body,
    )
    try:
        resp = _sg_client().send(mail)
        ok = 200 <= resp.status_code < 300
        target_status_id = sent.id if ok else error.id
        err_text = None if ok else f"SendGrid status {resp.status_code}: {resp.body}"
        if err_text:
            logger.error(err_text)
        for n in notifications:
            n.status_id = target_status_id
            if err_text:
                n.error_message = err_text
    except Exception as e: 
        err_text = str(e)
        logger.exception("SendGrid send failed (user change): %s", err_text)
        for n in notifications:
            n.status_id = error.id
            n.error_message = err_text
    db.commit()
