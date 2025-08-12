from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from ..database.core import Base 

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer,primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    users = relationship("UserRole", back_populates="role")
    permissions = relationship("RolePermission", back_populates="role")
    
    def __repr__(self):
        return f"<Role(name='{self.name}', description='{self.description}')>"
