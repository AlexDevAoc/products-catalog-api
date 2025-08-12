from sqlalchemy import Column, Integer, Text, DateTime, func
from sqlalchemy.orm import relationship

from ..database.core import Base 


class NotificationStatus(Base):
    __tablename__ = 'notification_status'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    admin_notifications = relationship("AdminNotification", back_populates="status")