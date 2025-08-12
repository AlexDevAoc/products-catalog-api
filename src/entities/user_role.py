from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ..database.core import Base 

class UserRole(Base):
    __tablename__ = 'user_roles'

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)

    user = relationship("User")
    role = relationship("Role", back_populates="users")
