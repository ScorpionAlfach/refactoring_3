from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base


class Order(Base):
    """Модель заказа в базе данных"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, index=True, nullable=False)
    product = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Order(id={self.id}, userId={self.userId}, product={self.product})>"
