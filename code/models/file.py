# models/file.py
from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    format = Column(String(50), nullable=False)
    path = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Связи
    exhibitions = relationship("Exhibition", back_populates="preview_file")
    contacts = relationship(
        "Contact",
        secondary="contact_file_associations",
        back_populates="files"
    )

    def __repr__(self):
        return f"<File(id={self.id}, name='{self.name}', format='{self.format}')>"