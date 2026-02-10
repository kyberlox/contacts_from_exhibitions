# schemas/base.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any

# Базовый класс для всех схем
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

# Схема с метаданными о времени создания/обновления
class TimestampSchema(BaseSchema):
    created_at: datetime
    updated_at: datetime

# Схема для пагинации
class PaginationParams(BaseSchema):
    skip: int = 0
    limit: int = 100
    order_by: Optional[str] = None
    order_desc: bool = False

# Схема для ответа с пагинацией
class PaginatedResponse(BaseSchema):
    total: int
    skip: int
    limit: int
    items: list