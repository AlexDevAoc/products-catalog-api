from pydantic import BaseModel
from typing import Optional, List

class AdminNotificationResponse(BaseModel):
    id: int
    change_log_id: Optional[int] = None  # product change log
    user_change_log_id: Optional[int] = None  # user change log
    sent_to: int
    sent_to_email: Optional[str] = None
    status: str
    message: str
    error_message: Optional[str] = None
    sent_at: str

    class Config:
        from_attributes = True

class AdminNotificationList(BaseModel):
    notifications: List[AdminNotificationResponse]
