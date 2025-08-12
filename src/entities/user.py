from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from ..database.core import Base 

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer,primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    status = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    sessions = relationship("UserSession", back_populates="user")
    change_logs = relationship("UserChangeLog", 
                                foreign_keys="[UserChangeLog.user_id]", 
                                back_populates="user")
    changes_made = relationship("UserChangeLog", 
                                foreign_keys="[UserChangeLog.changed_by]", 
                                back_populates="changed_by_user")
    
    def __repr__(self):
        return f"<User(email='{self.email}', first_name='{self.first_name}', last_name='{self.last_name}')>"