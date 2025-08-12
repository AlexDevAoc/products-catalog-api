from pydantic import BaseModel
from typing import Optional


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[bool] = True


class RoleCreate(RoleBase):
    name: str  


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = None


class RoleResponse(RoleBase):
    id: int

    class Config:
        from_attributes = True


class AssignRoleRequest(BaseModel):
    user_id: int
    role_id: int
