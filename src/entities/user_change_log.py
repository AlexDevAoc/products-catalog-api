from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship

from ..database.core import Base 

class UserChangeLog(Base):
    __tablename__ = 'user_change_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_id = Column(Integer, ForeignKey("actions_status.id"), nullable=False)
    field_changed = Column(Text, nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_at = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship("User", foreign_keys=[user_id], back_populates="change_logs")
    changed_by_user = relationship("User", foreign_keys=[changed_by], back_populates="changes_made")
    action = relationship("ActionStatus", back_populates="user_changes")