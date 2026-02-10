# schemas/file.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from .base import BaseSchema, TimestampSchema

# Базовые схемы
class FileBase(BaseSchema):
    name: str = Field(..., max_length=255, description="Название файла")
    format: str = Field(..., max_length=50, description="Формат файла")
    path: str = Field(..., description="Путь к файлу")
    url: str = Field(..., description="URL файла без домена")

# Создание файла
class FileCreate(FileBase):
    pass

# Обновление файла
class FileUpdate(BaseSchema):
    name: Optional[str] = Field(None, max_length=255)
    format: Optional[str] = Field(None, max_length=50)
    path: Optional[str] = None
    url: Optional[str] = None

# Полная схема файла (для ответа)
class File(FileBase, TimestampSchema):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Облегченная схема для вложений
class FileShort(BaseSchema):
    id: int
    name: str
    format: str
    url: str

# Схема для создания файла через API
class FileCreateRequest(BaseModel):
    filename: str
    content_type: str
    file_size: int