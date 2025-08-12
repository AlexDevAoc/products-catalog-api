from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from ..database.core import Base 

class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer,primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    roles = relationship("RolePermission", back_populates="permission")

    def __repr__(self):
        return f"<Permission(name={self.name}, description={self.description})>"