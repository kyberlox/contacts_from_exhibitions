# models/user.py
from sqlalchemy import Column, String, Boolean, Integer, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False, index=True)
    position = Column(String(255), nullable=True, index=True)
    department = Column(String(255), nullable=True, index=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Связи
    created_contacts = relationship(
        "Contact",
        back_populates="author",
        foreign_keys="Contact.author_id"
    )
    validated_contacts = relationship(
        "Contact",
        back_populates="validator",
        foreign_keys="Contact.validated_by_id"
    )

    def __repr__(self):
        return f"<User(id={self.id}, full_name='{self.full_name}', is_admin={self.is_admin})>"