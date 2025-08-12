from pydantic import BaseModel
from typing import Optional, List


class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[bool] = True


class PermissionCreate(PermissionBase):
    name: str


class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = None


class PermissionResponse(PermissionBase):
    id: int

    class Config:
        from_attributes = True


class AssignPermissionRequest(BaseModel):
    role_id: int
    permission_id: int


class RolePermissionsResponse(BaseModel):
    role_id: int
    permissions: List[PermissionResponse]


class UserPermissionsResponse(BaseModel):
    user_id: int
    permissions: List[PermissionResponse]
