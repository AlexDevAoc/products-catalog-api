from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductViewResponse(BaseModel):
    product_id: int
    view_count: int
    last_viewed_at: Optional[datetime]| None = None
    class Config:
        from_attributes = True
