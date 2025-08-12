from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.entities.product_view import ProductView
from src.entities.product import Product
from sqlalchemy import func

NOT_FOUND = "Product view not found"


def get_or_create(db: Session, product_id: int) -> ProductView:
    pv = db.query(ProductView).filter(ProductView.product_id == product_id).first()
    if not pv:
        # ensure product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        pv = ProductView(product_id=product_id, view_count=0)
        db.add(pv)
        db.commit(); db.refresh(pv)
    return pv


def increment_view(db: Session, product_id: int) -> ProductView:
    pv = get_or_create(db, product_id)
    pv.view_count += 1
    pv.last_viewed_at = func.now()
    db.commit(); db.refresh(pv)
    return pv


def get_view(db: Session, product_id: int) -> ProductView:
    pv = db.query(ProductView).filter(ProductView.product_id == product_id).first()
    if not pv:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    return pv


def list_views(db: Session):
    return db.query(ProductView).all()
