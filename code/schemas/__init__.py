# schemas/__init__.py
# Реэкспорт всех схем для удобного импорта
from typing import Optional, List
from datetime import date, datetime

# Base schemas
from .base import BaseSchema, TimestampSchema, PaginationParams, PaginatedResponse

# File schemas
from .file import (
    FileBase,
    FileCreate,
    FileUpdate,
    File,
    FileShort,
    FileCreateRequest
)

# Exhibition schemas
from .exhibition import (
    ExhibitionBase,
    ExhibitionCreate,
    ExhibitionUpdate,
    Exhibition,
    ExhibitionWithContacts,
    ExhibitionAdmin,
    ExhibitionFilter,
    ExhibitionSimple,
    ExhibitionWithContactsSimple
)

# Contact schemas
from .contact import (
    ContactBase,
    ContactCreate,
    ContactUpdate,
    Contact,
    ContactShort,
    ContactList,
    ContactWithExhibition,
    ContactFilter,
    ContactSearch,
    ContactImport,
    ContactBatchCreate,
    ContactExport,
    ContactStats,
    ContactDuplicateCheck,
    ContactDuplicateResponse
)

# Для решения циклических зависимостей
# Определяем классы, которые были использованы в аннотациях
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .exhibition import ExhibitionShort
    from .contact import ContactShort

# Определяем короткие схемы после импорта
from pydantic import Field
from .base import BaseSchema

class ExhibitionShort(BaseSchema):
    id: int
    title: str
    description: Optional[str] = None
    is_active: bool = True
    start_date: date
    end_date: date
    preview_file: Optional[FileShort] = None

    class Config:
        from_attributes = True

class ContactShort(BaseSchema):
    id: int
    title: str
    full_name: str
    phone_number: str
    created_at: str

# Обновляем Forward References
ExhibitionWithContacts.model_rebuild()
ContactWithExhibition.model_rebuild()

__all__ = [
    # Base
    "BaseSchema",
    "TimestampSchema",
    "PaginationParams",
    "PaginatedResponse",

    # File
    "FileBase",
    "FileCreate",
    "FileUpdate",
    "File",
    "FileShort",
    "FileCreateRequest",

    # Exhibition
    "ExhibitionBase",
    "ExhibitionCreate",
    "ExhibitionUpdate",
    "Exhibition",
    "ExhibitionWithContacts",
    "ExhibitionAdmin",
    "ExhibitionFilter",
    "ExhibitionShort",
    "ExhibitionSimple",
    "ExhibitionWithContactsSimple",

    # Contact
    "ContactBase",
    "ContactCreate",
    "ContactUpdate",
    "Contact",
    "ContactShort",
    "ContactList",
    "ContactWithExhibition",
    "ContactFilter",
    "ContactSearch",
    "ContactImport",
    "ContactBatchCreate",
    "ContactExport",
    "ContactStats",
    "ContactDuplicateCheck",
    "ContactDuplicateResponse",
]