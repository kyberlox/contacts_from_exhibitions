# schemas/contact.py
from pydantic import BaseModel, Field, ConfigDict, field_validator, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
import re
from .base import BaseSchema, TimestampSchema
from .exhibition import ExhibitionShort
from .user import UserShort

# Базовые схемы
class ContactBase(BaseSchema):
    title: str = Field(..., max_length=200, description="Название контакта (компания)")
    description: Optional[str] = Field(None, description="Дополнительное описание")
    full_name: str = Field(..., max_length=255, description="ФИО контакта")
    position: str = Field(..., max_length=255, description="Должность контакта")
    email: EmailStr = Field(..., max_length=255, description="Email контакта")
    phone_number: str = Field(..., max_length=50, description="Номер телефона")
    exhibition_id: int = Field(..., description="ID выставки")

# Создание контакта
class ContactCreate(ContactBase):
    questionnaire: Dict[str, Any] = Field(
        default_factory=dict,
        description="Анкета в формате JSON"
    )

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        # Базовая валидация номера телефона
        phone_regex = r'^[\d\s\-\+\(\)\.]+$'
        if not re.match(phone_regex, v):
            raise ValueError('Номер телефона содержит недопустимые символы')

        return v

# Обновление контакта
class ContactUpdate(BaseSchema):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    full_name: Optional[str] = Field(None, max_length=255)
    position: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=50)
    questionnaire: Optional[Dict[str, Any]] = None
    notes: Optional[str] = Field(None, description="Заметки администратора")
    is_validated: Optional[bool] = Field(None, description="Валидирован ли контакт администратором")

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        if v is None:
            return v

        phone_regex = r'^[\d\s\-\+\(\)\.]+$'
        if not re.match(phone_regex, v):
            raise ValueError('Номер телефона содержит недопустимые символы')

        digits = re.sub(r'\D', '', v)
        if len(digits) < 10:
            raise ValueError('Номер телефона слишком короткий')

        return v

# Полная схема контакта
class Contact(ContactBase, TimestampSchema):
    id: int
    author_id: Optional[int] = None
    is_validated: bool = False
    validated_by_id: Optional[int] = None
    validated_at: Optional[datetime] = None
    notes: Optional[str] = None
    author: Optional[UserShort] = None
    validator: Optional[UserShort] = None
    exhibition: Optional["ExhibitionShort"] = None

    model_config = ConfigDict(from_attributes=True)

class ContactAdminUpdate(BaseSchema):
    """Схема для административного обновления контакта"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    full_name: Optional[str] = Field(None, max_length=255)
    position: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=50)
    questionnaire: Optional[Dict[str, Any]] = None
    exhibition_id: Optional[int] = None
    notes: Optional[str] = None
    is_validated: Optional[bool] = None

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        if v is None:
            return v

        phone_regex = r'^[\d\s\-\+\(\)\.]+$'
        if not re.match(phone_regex, v):
            raise ValueError('Номер телефона содержит недопустимые символы')

        digits = re.sub(r'\D', '', v)
        if len(digits) < 10:
            raise ValueError('Номер телефона слишком короткий')

        return v

# Облегченная схема контакта
class ContactShort(BaseSchema):
    id: int
    title: str
    full_name: str
    position: str
    email: str
    phone_number: str
    created_at: datetime

# Схема контакта для списка
class ContactList(BaseSchema):
    id: int
    title: str
    full_name: str
    position: str
    email: str
    phone_number: str
    exhibition_title: Optional[str] = None
    created_at: datetime

# Схема контакта с деталями выставки
class ContactWithExhibition(Contact):
    exhibition: Optional["ExhibitionShort"] = None

# Схема для фильтрации контактов
class ContactFilter(BaseSchema):
    title: Optional[str] = None
    full_name: Optional[str] = None
    position: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    exhibition_id: Optional[int] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None

    @field_validator('phone_number')
    @classmethod
    def clean_phone_number(cls, v):
        if v:
            # Очищаем номер для поиска
            return re.sub(r'\D', '', v)
        return v

    @field_validator('email')
    @classmethod
    def email_to_lowercase(cls, v):
        if v:
            return v.lower()
        return v

# Схема для поиска контактов
class ContactSearch(BaseSchema):
    query: Optional[str] = Field(None, description="Поиск по всем текстовым полям")
    exhibition_id: Optional[int] = None

    @field_validator('query')
    @classmethod
    def validate_query_length(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('Поисковый запрос должен содержать минимум 2 символа')
        return v.strip() if v else None

# Схема для импорта контактов
class ContactImport(BaseSchema):
    title: str
    full_name: str
    position: str
    email: EmailStr
    phone_number: str
    description: Optional[str] = None
    exhibition_id: Optional[int] = Field(None, description="ID выставки, если известен")
    questionnaire: Dict[str, Any] = Field(default_factory=dict)

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        phone_regex = r'^[\d\s\-\+\(\)\.]+$'
        if not re.match(phone_regex, v):
            raise ValueError('Номер телефона содержит недопустимые символы')

        digits = re.sub(r'\D', '', v)
        if len(digits) < 10:
            raise ValueError('Номер телефона слишком короткий')

        return v

    @field_validator('email')
    @classmethod
    def email_to_lowercase(cls, v):
        return v.lower()

# Схема для массового создания контактов
class ContactBatchCreate(BaseSchema):
    exhibition_id: int
    contacts: List[ContactImport]

# Схема для экспорта контактов
class ContactExport(BaseSchema):
    id: int
    title: str
    description: Optional[str]
    full_name: str
    position: str
    email: str
    phone_number: str
    exhibition_title: Optional[str]
    exhibition_start_date: Optional[datetime]
    exhibition_end_date: Optional[datetime]
    created_at: datetime
    questionnaire: Dict[str, Any]

# Схема для статистики по контактам
class ContactStats(BaseSchema):
    total_contacts: int
    contacts_by_exhibition: Dict[str, int]
    contacts_by_position: Dict[str, int]
    contacts_last_week: int
    contacts_today: int

# Схема для проверки дубликатов контактов
class ContactDuplicateCheck(BaseSchema):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    exhibition_id: Optional[int] = None

    @field_validator('phone_number')
    @classmethod
    def clean_phone_for_check(cls, v):
        if v:
            return re.sub(r'\D', '', v)
        return v

    @field_validator('email')
    @classmethod
    def email_to_lowercase(cls, v):
        if v:
            return v.lower()
        return v

# Схема ответа при проверке дубликатов
class ContactDuplicateResponse(BaseSchema):
    is_duplicate: bool
    duplicate_fields: List[str] = Field(default_factory=list)
    existing_contact: Optional[ContactShort] = None