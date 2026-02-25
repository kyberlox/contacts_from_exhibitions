# models/contact.py
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum, Table, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from sqlalchemy.sql import func

from .base import Base

# Enum для типов файлов контакта
class ContactFileType(str, enum.Enum):
    BUSINESS_CARD_FRONT = "business_card_front"
    BUSINESS_CARD_BACK = "business_card_back"
    DOCUMENT = "document"
    OTHER = "other"

# Таблица для связи контактов и файлов (многие-ко-многим)
contact_file_association = Table(
    'contact_file_associations',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('contact_id', Integer, ForeignKey('contacts.id', ondelete='CASCADE')),
    Column('file_id', Integer, ForeignKey('files.id', ondelete='CASCADE')),
    Column('file_type', Enum(ContactFileType), default=ContactFileType.OTHER),
    Column('created_at', DateTime, server_default=func.now())
)

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    full_name = Column(String(255), nullable=False, index=True)
    position = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    phone_number = Column(String(255), nullable=False, index=True)
    city = Column(String(255), nullable=True, index=True)
    questionnaire = Column(JSONB, nullable=False, default={})
    exhibition_id = Column(
        Integer,
        ForeignKey("exhibitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    author_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    is_validated = Column(Boolean, default=False, nullable=False, index=True)
    validated_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    validated_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)  # Заметки администратора
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Связи
    exhibition = relationship("Exhibition", back_populates="contacts")
    author = relationship("User", back_populates="created_contacts", foreign_keys=[author_id])
    validator = relationship("User", foreign_keys=[validated_by_id])

    # Связь с файлами через ассоциативную таблицу
    files = relationship(
        "File",
        secondary=contact_file_association,
        back_populates="contacts",
        cascade="all, delete"
    )