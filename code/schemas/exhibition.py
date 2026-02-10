# schemas/exhibition.py
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from .base import BaseSchema, TimestampSchema
from .file import FileShort

# Базовые схемы
class ExhibitionBase(BaseSchema):
    title: str = Field(..., max_length=200, description="Название выставки")
    description: Optional[str] = Field(None, description="Описание выставки")
    start_date: date = Field(..., description="Дата начала выставки")
    end_date: date = Field(..., description="Дата окончания выставки")
    preview_file_id: Optional[int] = Field(None, description="ID превью файла")

# Создание выставки
class ExhibitionCreate(ExhibitionBase):
    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, end_date: date, values):
        if 'start_date' in values.data and end_date < values.data['start_date']:
            raise ValueError('Дата окончания не может быть раньше даты начала')
        return end_date

# Обновление выставки
class ExhibitionUpdate(BaseSchema):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    preview_file_id: Optional[int] = None

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, end_date: date, values):
        if 'start_date' in values.data and end_date and values.data['start_date']:
            if end_date < values.data['start_date']:
                raise ValueError('Дата окончания не может быть раньше даты начала')
        return end_date

# Полная схема выставки
class Exhibition(ExhibitionBase, TimestampSchema):
    id: int
    preview_file: Optional[FileShort] = None
    contacts_count: Optional[int] = Field(0, description="Количество контактов")

    model_config = ConfigDict(from_attributes=True)

# Схема выставки с контактами
class ExhibitionWithContacts(Exhibition):
    contacts: List["ContactShort"] = []

# Схема выставки с деталями для администратора
class ExhibitionAdmin(ExhibitionWithContacts):
    pass

# Схема для фильтрации выставок
class ExhibitionFilter(BaseSchema):
    title: Optional[str] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    end_date_from: Optional[date] = None
    end_date_to: Optional[date] = None
    active: Optional[bool] = None

    @field_validator('active', mode='before')
    @classmethod
    def set_active_filter(cls, v, values):
        if v is True:
            today = date.today()
            return {
                'start_date_lte': today,
                'end_date_gte': today
            }
        return None

class ExhibitionShort(BaseSchema):
    id: int
    title: str
    start_date: date
    end_date: date
    preview_file: Optional[FileShort] = None

    class Config:
        from_attributes = True

# В schemas/exhibition.py добавьте простые схемы без сложных отношений:

class ExhibitionSimple(BaseSchema):
    id: int
    title: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    preview_file_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ExhibitionWithContactsSimple(BaseSchema):
    id: int
    title: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    preview_file_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    contacts: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
