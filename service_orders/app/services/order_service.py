from sqlalchemy.orm import Session
from typing import Optional, List
from ..models import Order
from ..schemas import OrderCreate, OrderUpdate
from ..redis_client import redis_client


class OrderService:
    """Сервис для работы с заказами"""
    
    @staticmethod
    def get_order_by_id(db: Session, order_id: int) -> Optional[dict]:
        """Получить заказ по ID с использованием кэша"""
        cache_key = f"order:{order_id}"
        
        # Проверяем кэш
        cached_order = redis_client.get(cache_key)
        if cached_order:
            print(f"✅ Cache HIT for {cache_key}")
            return cached_order
        
        # Запрос в БД
        print(f"❌ Cache MISS for {cache_key}")
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return None
        
        # Преобразуем в dict и сохраняем в кэш
        order_dict = {
            "id": order.id,
            "userId": order.userId,
            "product": order.product,
            "quantity": order.quantity,
            "created_at": order.created_at.isoformat()
        }
        
        # Сохраняем в кэш на 5 минут
        redis_client.set(cache_key, order_dict, expire=300)
        
        return order_dict
    
    @staticmethod
    def get_all_orders(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Order]:
        """Получить список заказов с фильтрацией по userId"""
        query = db.query(Order)
        
        if user_id is not None:
            query = query.filter(Order.userId == user_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_order(db: Session, order_data: OrderCreate) -> Order:
        """Создать новый заказ"""
        order = Order(**order_data.model_dump())
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def update_order(db: Session, order_id: int, order_data: OrderUpdate) -> Optional[Order]:
        """Обновить заказ с инвалидацией кэша"""
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return None
        
        update_data = order_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(order, key, value)
        
        db.commit()
        db.refresh(order)
        
        # Инвалидируем кэш
        redis_client.delete(f"order:{order_id}")
        print(f"🗑️  Cache invalidated for order:{order_id}")
        
        return order
    
    @staticmethod
    def delete_order(db: Session, order_id: int) -> Optional[Order]:
        """Удалить заказ с инвалидацией кэша"""
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return None
        
        db.delete(order)
        db.commit()
        
        # Инвалидируем кэш
        redis_client.delete(f"order:{order_id}")
        print(f"🗑️  Cache invalidated for order:{order_id}")
        
        return order


order_service = OrderService()
