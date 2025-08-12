from sqlalchemy import Column, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

from ..database.core import Base 

class ProductView(Base):
    __tablename__ = 'product_views'

    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    view_count = Column(Integer, default=0, nullable=False)
    last_viewed_at = Column(DateTime, nullable=False, server_default=func.now())

    product = relationship("Product", back_populates="views")