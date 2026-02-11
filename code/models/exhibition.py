# models/exhibition.py
from sqlalchemy import Column, String, Text, Date, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base

class Exhibition(Base):
    __tablename__ = "exhibitions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)  # текущая выставка
    description = Column(Text)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    preview_file_id = Column(
        Integer,
        ForeignKey("files.id", ondelete="SET NULL"),
        nullable=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Связи
    preview_file = relationship("File", foreign_keys=[preview_file_id], back_populates="exhibitions")
    contacts = relationship("Contact", back_populates="exhibition", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Exhibition(id={self.id}, title='{self.title}', dates={self.start_date}-{self.end_date})>"