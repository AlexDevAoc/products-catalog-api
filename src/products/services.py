from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models
from src.entities.product import Product
from src.entities.brand import Brand
from src.entities.user import User
from ..roles.services import get_user_role, ANONYMOUS_ROLE
from ..product_views import services as pv_services
from ..product_change_logs import services as pcl_services


def list_products(db: Session, user_id: int):
    products = db.query(Product).all()
    role = get_user_role(db, user_id)
    if role.name == ANONYMOUS_ROLE:
        for product in products:
            pv_services.increment_view(db, product.id)
    return products


def get_product(db: Session, product_id: int, user_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    role =  get_user_role(db, user_id)
    if role.name == ANONYMOUS_ROLE:
        pv_services.increment_view(db, product.id)
    return product


def create_product(db: Session, product_in: models.ProductCreate, creator_id: int) -> Product:
    if db.query(Product).filter(Product.name == product_in.name).first():
        raise HTTPException(status_code=400, detail="Product name already exists")
    if db.query(Product).filter(Product.sku == product_in.sku).first():
        raise HTTPException(status_code=400, detail="Product SKU already exists")
    if not db.query(Brand).filter(Brand.id == product_in.brand_id).first():
        raise HTTPException(status_code=404, detail="Brand not found")
    if not db.query(User).filter(User.id == creator_id).first():
        raise HTTPException(status_code=404, detail="Creator user not found")
    product = Product(
        sku=product_in.sku,
        name=product_in.name,
        description=product_in.description,
        price=product_in.price,
        brand_id=product_in.brand_id,
        status=product_in.status if product_in.status is not None else True,
        created_by=creator_id
    )
    db.add(product)
    db.commit(); db.refresh(product)
    return product


def update_product(db: Session, product_id: int, product_in: models.ProductUpdate, user_id: int) -> Product:
    product = get_product(db, product_id, user_id)
    before = {
        "name": product.name,
        "sku": product.sku,
        "description": product.description,
        "price": str(product.price),
        "brand_id": product.brand_id,
        "status": product.status,
    }
    if product_in.name is not None and product_in.name != product.name:
        if db.query(Product).filter(Product.name == product_in.name).first():
            raise HTTPException(status_code=400, detail="Product name already exists")
        product.name = product_in.name
    if product_in.sku is not None and product_in.sku != product.sku:
        if db.query(Product).filter(Product.sku == product_in.sku).first():
            raise HTTPException(status_code=400, detail="Product SKU already exists")
        product.sku = product_in.sku
    if product_in.description is not None:
        product.description = product_in.description
    if product_in.price is not None:
        product.price = product_in.price
    if product_in.brand_id is not None:
        if not db.query(Brand).filter(Brand.id == product_in.brand_id).first():
            raise HTTPException(status_code=404, detail="Brand not found")
        product.brand_id = product_in.brand_id
    if product_in.status is not None:
        product.status = product_in.status
    db.commit(); db.refresh(product)
    after = {
        "name": product.name,
        "sku": product.sku,
        "description": product.description,
        "price": str(product.price),
        "brand_id": product.brand_id,
        "status": product.status,
    }
    pcl_services.diff_and_log(db, product, before, after, user_id, action_name="UPDATE_PRODUCT")
    return product


def soft_delete_product(db: Session, product_id: int, user_id: int) -> None:
    product = get_product(db, product_id, user_id)
    before = {"status": product.status}
    product.status = False
    db.commit(); db.refresh(product)
    after = {"status": product.status}
    pcl_services.diff_and_log(db, product, before, after, user_id, action_name="DELETE_PRODUCT")
