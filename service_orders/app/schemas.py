from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class OrderBase(BaseModel):
    """Базовая схема заказа"""
    userId: int = Field(..., gt=0)
    product: str = Field(..., min_length=1, max_length=200)
    quantity: int = Field(default=1, gt=0)


class OrderCreate(OrderBase):
    """Схема для создания заказа"""
    pass


class OrderUpdate(BaseModel):
    """Схема для обновления заказа"""
    userId: Optional[int] = Field(None, gt=0)
    product: Optional[str] = Field(None, min_length=1, max_length=200)
    quantity: Optional[int] = Field(None, gt=0)


class OrderResponse(OrderBase):
    """Схема ответа с заказом"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
