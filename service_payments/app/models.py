from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from datetime import datetime
import enum
from .database import Base


class PaymentStatus(str, enum.Enum):
    """Статусы платежа"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Payment(Base):
    """Модель платежа в базе данных"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default=PaymentStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Payment(id={self.id}, order_id={self.order_id}, amount={self.amount}, status={self.status})>"
