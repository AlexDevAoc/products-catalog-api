import os
from typing import List, Iterable
from sqlalchemy.orm import Session
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from src.entities.product_change_log import ProductChangeLog
from src.entities.admin_notification import AdminNotification
from src.entities.product import Product
from src.entities.notification_status import NotificationStatus
from src.entities.user import User
from src.entities.user_role import UserRole
from src.entities.role import Role
from src.roles.services import ADMIN_ROLE

logger = logging.getLogger(__name__)

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
NOTIFICATION_SENDER = os.getenv("NOTIFICATION_SENDER")  # e.g. verified sender
ENABLE_EMAIL_NOTIFICATIONS = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "false").lower() == "true"

NOTIF_STATUS_PENDING = "PENDING"
NOTIF_STATUS_SENT = "SENT"
NOTIF_STATUS_ERROR = "ERROR"


def _get_or_create_status(db: Session, name: str) -> NotificationStatus:
    status = db.query(NotificationStatus).filter(NotificationStatus.name == name).first()
    if status:
        return status
    status = NotificationStatus(name=name, description=name)
    db.add(status)
    db.commit(); db.refresh(status)
    return status


def _sg_client():
    return SendGridAPIClient(SENDGRID_API_KEY)


def _admin_user_ids(db: Session) -> List[int]:
    admin_role = db.query(Role).filter(Role.name == ADMIN_ROLE).first()
    if not admin_role:
        return []
    user_roles = db.query(UserRole).filter(UserRole.role_id == admin_role.id).all()
    return [ur.user_id for ur in user_roles]


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


def _build_email_content(product_id: int, product_name: str, changer_email: str, diffs: Iterable[ProductChangeLog]) -> tuple[str, str]:
    diffs_list = list(diffs)
    if not diffs_list:
        return ("", "")
    if len(diffs_list) == 1:
        d = diffs_list[0]
        subject = f"Product '{product_name}' (#{product_id}) field {d.field_changed} updated"
    else:
        subject = f"Product '{product_name}' (#{product_id}) updated ({len(diffs_list)} changes)"
    lines = []
    for d in diffs_list:
        lines.append(f"- {d.field_changed}: {d.old_value} -> {d.new_value}")
    body = (
        f"Product '{product_name}' (ID {product_id}) updated by {changer_email}.\n\nChanges:\n" + "\n".join(lines)
    )
    return subject, body


def send_admin_notifications_for_product_change(db: Session, change_logs: List[ProductChangeLog]):
    """Send a single email per update operation (may include multiple field diffs)."""
    if not change_logs:
        return
    if not _validate_config():
        return
    product_id = change_logs[0].product_id
    changed_by = change_logs[0].changed_by
    admin_ids = _admin_user_ids(db)
    if not admin_ids:
        logger.info("No admin users to notify")
        return
    users = db.query(User).filter(User.id.in_(admin_ids)).all()
    active_users = [u for u in users if u.status]
    if not active_users:
        logger.info("No active admin users to notify")
        return

    product = db.query(Product).filter(Product.id == product_id).first()
    changer = db.query(User).filter(User.id == changed_by).first()
    product_name = product.name if product else f"#{product_id}"
    changer_email = changer.email if changer else f"user:{changed_by}"
    subject, body = _build_email_content(product_id, product_name, changer_email, change_logs)
    if not subject:
        return

    pending_status = _get_or_create_status(db, NOTIF_STATUS_PENDING)
    sent_status = _get_or_create_status(db, NOTIF_STATUS_SENT)
    error_status = _get_or_create_status(db, NOTIF_STATUS_ERROR)

    # Create pending notifications
    notifications: List[AdminNotification] = []
    for u in active_users:
        notif = AdminNotification(
            change_log_id=change_logs[-1].id,  # reference last change id
            sent_to=u.id,
            status_id=pending_status.id,
            message=body
        )
        db.add(notif)
        notifications.append(notif)
    db.commit()

    to_addresses = [u.email for u in active_users]
    mail = Mail(
        from_email=NOTIFICATION_SENDER,
        to_emails=to_addresses,
        subject=subject,
        plain_text_content=body,
    )
    try:
        resp = _sg_client().send(mail)
        if 200 <= resp.status_code < 300:
            for n in notifications:
                n.status_id = sent_status.id
        else:
            err = f"SendGrid status {resp.status_code}: {resp.body}"
            logger.error(err)
            for n in notifications:
                n.status_id = error_status.id
                n.error_message = err
    except Exception as e:  # broad catch for sendgrid
        err = str(e)
        logger.exception("SendGrid send failed: %s", err)
        for n in notifications:
            n.status_id = error_status.id
            n.error_message = err
    db.commit()
