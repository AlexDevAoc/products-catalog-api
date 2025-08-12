from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from ..database.core import Base 

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer,primary_key=True, autoincrement=True)
    sku = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    status = Column(Boolean, default=True, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    brand = relationship("Brand", back_populates="products")
    creator = relationship("User", back_populates="products")
    views = relationship("ProductView", back_populates="product", uselist=False)
