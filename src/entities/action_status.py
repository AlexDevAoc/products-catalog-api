from sqlalchemy import Column, Integer, DateTime, String, func
from sqlalchemy.orm import relationship

from ..database.core import Base 

class ActionStatus(Base):
    __tablename__ = "actions_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(10), nullable=False)
    description = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    product_changes = relationship("ProductChangeLog", back_populates="action")
    user_changes = relationship("UserChangeLog", back_populates="action")