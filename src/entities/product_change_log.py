from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship

from ..database.core import Base 


class ProductChangeLog(Base):
    __tablename__ = 'product_change_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_id = Column(Integer, ForeignKey("actions_status.id"), nullable=False)
    field_changed = Column(Text, nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_at = Column(DateTime, nullable=False, server_default=func.now())

    product = relationship("Product", back_populates="change_logs")
    changed_by_user = relationship("User")
    action = relationship("ActionStatus", back_populates="product_changes")
    admin_notifications = relationship("AdminNotification", back_populates="change_log")