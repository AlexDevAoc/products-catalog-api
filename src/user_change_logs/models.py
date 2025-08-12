from pydantic import BaseModel
from typing import Optional, List


class ActionStatusBase(BaseModel):
    name: str
    description: str


class ActionStatusCreate(ActionStatusBase):
    pass


class ActionStatusResponse(ActionStatusBase):
    id: int

    class Config:
        from_attributes = True


class UserChangeLogResponse(BaseModel):
    id: int
    user_id: int
    changed_by: int
    action_id: int
    action_name: Optional[str] = None
    field_changed: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_at: str

    class Config:
        from_attributes = True


class UserChangeLogList(BaseModel):
    logs: List[UserChangeLogResponse]
