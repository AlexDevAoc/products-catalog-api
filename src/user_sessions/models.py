from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserSessionResponse(BaseModel):
    id: int
    user_id: int
    is_anonymous: bool
    login_at: datetime
    logout_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserSessionCloseResponse(BaseModel):
    id: int
    logout_at: str | None


class UserActiveSessionResponse(BaseModel):
    has_active: bool
    session_id: int | None = None
