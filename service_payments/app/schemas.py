from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class PaymentStatus(str, Enum):
    """Статусы платежа"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentBase(BaseModel):
    """Базовая схема платежа"""
    order_id: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)


class PaymentCreate(PaymentBase):
    """Схема для создания платежа"""
    pass


class PaymentUpdate(BaseModel):
    """Схема для обновления платежа"""
    status: Optional[PaymentStatus] = None


class PaymentResponse(PaymentBase):
    """Схема ответа с платежом"""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
