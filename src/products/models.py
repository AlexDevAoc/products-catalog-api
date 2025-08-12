from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    price: Decimal
    brand_id: int
    status: Optional[bool] = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    brand_id: Optional[int] = None
    status: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    created_by: int
    class Config:
        from_attributes = True
