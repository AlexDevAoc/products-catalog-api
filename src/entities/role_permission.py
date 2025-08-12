from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ..database.core import Base 

class RolePermission(Base):
    __tablename__ = 'role_permissions'

    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), primary_key=True)

    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")