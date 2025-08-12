from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import relationship

from ..database.core import Base 

class UserSession(Base):
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_anonymous = Column(Boolean, default=False, nullable=False)
    login_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    logout_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="sessions")
