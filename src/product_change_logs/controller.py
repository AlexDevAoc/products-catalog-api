from fastapi import APIRouter, Depends
from typing import List
from ..database.core import DbSession
from ..roles.services import require_admin
from . import services, models

router = APIRouter(prefix="/product-change-logs", tags=["ProductChangeLogs"], dependencies=[Depends(require_admin)])


@router.get("/", response_model=List[models.ProductChangeLogResponse])
def list_all(db: DbSession):
    logs = services.list_all_logs(db)
    return services.enrich_with_actions(db, logs)


@router.get("/product/{product_id}", response_model=List[models.ProductChangeLogResponse])
def list_by_product(product_id: int, db: DbSession):
    logs = services.list_logs_by_product(db, product_id)
    return services.enrich_with_actions(db, logs)
