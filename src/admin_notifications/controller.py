from fastapi import APIRouter, Depends
from typing import List
from ..database.core import DbSession
from ..roles.services import require_admin
from . import services, models
from ..auth.service import CurrentUser

router = APIRouter(prefix="/admin-notifications", tags=["AdminNotifications"], dependencies=[Depends(require_admin)])

@router.get("/", response_model=List[models.AdminNotificationResponse])
def list_all(db: DbSession):
    notifs = services.list_notifications(db)
    return services.enrich(db, notifs)

@router.get("/me", response_model=List[models.AdminNotificationResponse], dependencies=[])  # require_admin already global
def my_notifications(current_user: CurrentUser, db: DbSession):
    notifs = services.list_notifications_by_user(db, current_user.user_id)
    return services.enrich(db, notifs)
