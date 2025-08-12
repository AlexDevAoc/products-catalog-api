from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship

from ..database.core import Base 


class AdminNotification(Base):
    __tablename__ = 'admin_notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    change_log_id = Column(Integer, ForeignKey("product_change_logs.id"), nullable=False)
    sent_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    sent_at = Column(DateTime, nullable=False, server_default=func.now())
    status_id = Column(Integer, ForeignKey("notification_status.id"), nullable=False)
    message = Column(Text, nullable=False)
    error_message = Column(Text, nullable=True)

    change_log = relationship("ProductChangeLog", back_populates="admin_notifications")
    sent_to_user = relationship("User", foreign_keys=[sent_to])
    status = relationship("NotificationStatus")