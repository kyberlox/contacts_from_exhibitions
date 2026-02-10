# schemas/users.py
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    full_name: str = Field(..., max_length=255, description="ФИО пользователя")
    position: Optional[str] = Field(None, max_length=255, description="Должность")
    department: Optional[str] = Field(None, max_length=255, description="Подразделение")

class UserCreate(UserBase):
    is_admin: bool = Field(False, description="Является ли администратором")

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    position: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=255)
    is_admin: Optional[bool] = None

class User(UserBase):
    id: int
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserShort(BaseModel):
    id: int
    full_name: str
    position: Optional[str] = None
    department: Optional[str] = None
    is_admin: bool

class UserSession(BaseModel):
    session_id: str = Field(..., description="Session ID из куки")

class ExternalUserInfo(BaseModel):
    full_name: str
    position: Optional[str] = None
    department: Optional[str] = None
    is_admin: bool = False