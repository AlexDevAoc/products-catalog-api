from pydantic import BaseModel
from typing import Optional

class BrandBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[bool] = True

class BrandCreate(BrandBase):
    name: str

class BrandUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = None

class BrandResponse(BrandBase):
    id: int
    class Config:
        from_attributes = True
