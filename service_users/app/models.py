from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base


class User(Base):
    """Модель пользователя в базе данных"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
