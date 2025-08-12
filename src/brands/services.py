from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models
from src.entities.brand import Brand


def list_brands(db: Session):
    return db.query(Brand).all()


def get_brand(db: Session, brand_id: int) -> Brand:
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


def create_brand(db: Session, brand_in: models.BrandCreate) -> Brand:
    exists = db.query(Brand).filter(Brand.name == brand_in.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Brand name already exists")
    brand = Brand(name=brand_in.name, description=brand_in.description, status=brand_in.status)
    db.add(brand)
    db.commit(); db.refresh(brand)
    return brand


def update_brand(db: Session, brand_id: int, brand_in: models.BrandUpdate) -> Brand:
    brand = get_brand(db, brand_id)
    if brand_in.name is not None and brand_in.name != brand.name:
        exists = db.query(Brand).filter(Brand.name == brand_in.name).first()
        if exists:
            raise HTTPException(status_code=400, detail="Brand name already exists")
        brand.name = brand_in.name
    if brand_in.description is not None:
        brand.description = brand_in.description
    if brand_in.status is not None:
        brand.status = brand_in.status
    db.commit(); db.refresh(brand)
    return brand


def soft_delete_brand(db: Session, brand_id: int) -> None:
    brand = get_brand(db, brand_id)
    brand.status = False
    db.commit()
