from pydantic import BaseModel
from typing import Optional, List


class ProductChangeLogResponse(BaseModel):
    id: int
    product_id: int
    changed_by: int
    action_id: int
    action_name: Optional[str] = None
    field_changed: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_at: str

    class Config:
        from_attributes = True


class ProductChangeLogList(BaseModel):
    logs: List[ProductChangeLogResponse]
