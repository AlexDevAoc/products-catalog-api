from sqlalchemy import Column, Integer, ForeignKey, Datetime, Boolean
from sqlalchemy.orm import relationship

from ..database.core import Base 

class UserSession(Base):
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_anonymous = Column(Boolean, default=False, nullable=False)
    login_at = Column(Datetime, nullable=False)
    logout_at = Column(Datetime, nullable=True)

    user = relationship("User", back_populates="sessions")
