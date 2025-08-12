from fastapi import APIRouter, Depends
from ..database.core import DbSession
from . import models, services
from ..auth.service import CurrentUser
from ..roles.services import require_anonymous_or_admin_read_get, require_admin

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=list[models.ProductResponse], dependencies=[Depends(require_anonymous_or_admin_read_get)])
def list_products(db: DbSession, current_user: CurrentUser):
    return services.list_products(db, user_id=current_user.user_id)


@router.get("/{product_id}", response_model=models.ProductResponse, dependencies=[Depends(require_anonymous_or_admin_read_get)])
def get_product(product_id: int, db: DbSession, current_user: CurrentUser):
    return services.get_product(db, product_id, user_id=current_user.user_id)


@router.post("/", response_model=models.ProductResponse, dependencies=[Depends(require_admin)])
def create_product(current_user: CurrentUser, product_in: models.ProductCreate, db: DbSession):
    return services.create_product(db, product_in, creator_id=current_user.user_id)


@router.put("/{product_id}", response_model=models.ProductResponse, dependencies=[Depends(require_admin)])
def update_product(product_id: int, product_in: models.ProductUpdate, db: DbSession, current_user: CurrentUser):
    return services.update_product(db, product_id, product_in, user_id=current_user.user_id)


@router.delete("/{product_id}", status_code=204, dependencies=[Depends(require_admin)])
def soft_delete_product(product_id: int, db: DbSession, current_user: CurrentUser):
    services.soft_delete_product(db, product_id, user_id=current_user.user_id)
    return None
