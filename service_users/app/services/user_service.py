from sqlalchemy.orm import Session
from typing import Optional, List
from ..models import User
from ..schemas import UserCreate, UserUpdate
from ..redis_client import redis_client


class UserService:
    """Сервис для работы с пользователями"""
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[dict]:
        """
        Получить пользователя по ID с использованием кэша
        
        Стратегия: Cache-Aside (Lazy Loading)
        1. Проверяем кэш
        2. Если нет - идём в БД
        3. Сохраняем в кэш
        """
        cache_key = f"user:{user_id}"
        
        # 1. Проверяем кэш
        cached_user = redis_client.get(cache_key)
        if cached_user:
            print(f"✅ Cache HIT for {cache_key}")
            return cached_user
        
        # 2. Запрос в БД
        print(f"❌ Cache MISS for {cache_key}")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        # 3. Преобразуем в dict и сохраняем в кэш
        user_dict = {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at.isoformat()
        }
        
        # Сохраняем в кэш на 5 минут
        redis_client.set(cache_key, user_dict, expire=300)
        
        return user_dict
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить список всех пользователей"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Создать нового пользователя"""
        user = User(**user_data.model_dump())
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """
        Обновить пользователя
        
        Важно: После обновления инвалидируем кэш!
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        # Обновляем только переданные поля
        update_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        
        # Инвалидируем кэш
        redis_client.delete(f"user:{user_id}")
        print(f"🗑️  Cache invalidated for user:{user_id}")
        
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> Optional[User]:
        """
        Удалить пользователя
        
        Важно: После удаления инвалидируем кэш!
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        db.delete(user)
        db.commit()
        
        # Инвалидируем кэш
        redis_client.delete(f"user:{user_id}")
        print(f"🗑️  Cache invalidated for user:{user_id}")
        
        return user


# Экспортируем экземпляр сервиса
user_service = UserService()
