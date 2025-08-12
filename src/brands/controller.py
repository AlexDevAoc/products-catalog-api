from fastapi import APIRouter, status, Depends
from typing import List
from ..database.core import DbSession
from . import models, services
from ..roles.services import require_admin

router = APIRouter(prefix="/brands", tags=["Brands"])

@router.get("/", response_model=List[models.BrandResponse])
def list_brands(db: DbSession):
    return services.list_brands(db)

@router.get("/{brand_id}", response_model=models.BrandResponse)
def get_brand(brand_id: int, db: DbSession):
    return services.get_brand(db, brand_id)

@router.post("/", response_model=models.BrandResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_brand(brand_in: models.BrandCreate, db: DbSession):
    return services.create_brand(db, brand_in)

@router.put("/{brand_id}", response_model=models.BrandResponse, dependencies=[Depends(require_admin)])
def update_brand(brand_id: int, brand_in: models.BrandUpdate, db: DbSession):
    return services.update_brand(db, brand_id, brand_in)

@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def soft_delete_brand(brand_id: int, db: DbSession):
    services.soft_delete_brand(db, brand_id)
