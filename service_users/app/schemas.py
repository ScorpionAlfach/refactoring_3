from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    pass


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class UserResponse(UserBase):
    """Схема ответа с пользователем"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
