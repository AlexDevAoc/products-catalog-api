from fastapi import APIRouter
from ..database.core import DbSession
from . import services, models

router = APIRouter(prefix="/product-views", tags=["ProductViews"])

@router.get("/", response_model=list[models.ProductViewResponse])
def list_product_views(db: DbSession):
    return services.list_views(db)

@router.get("/{product_id}", response_model=models.ProductViewResponse)
def get_product_view(product_id: int, db: DbSession):
    return services.get_view(db, product_id)
