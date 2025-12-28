from sqlalchemy.orm import Session
from typing import Optional, List
import random
from ..models import Payment, PaymentStatus
from ..schemas import PaymentCreate, PaymentUpdate
from ..redis_client import redis_client


class PaymentService:
    """Сервис для работы с платежами"""
    
    @staticmethod
    def get_payment_by_id(db: Session, payment_id: int) -> Optional[dict]:
        """Получить платеж по ID с кэшированием"""
        cache_key = f"payment:{payment_id}"
        
        cached_payment = redis_client.get(cache_key)
        if cached_payment:
            print(f"✅ Cache HIT for {cache_key}")
            return cached_payment
        
        print(f"❌ Cache MISS for {cache_key}")
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            return None
        
        payment_dict = {
            "id": payment.id,
            "order_id": payment.order_id,
            "amount": payment.amount,
            "status": payment.status,
            "created_at": payment.created_at.isoformat(),
            "updated_at": payment.updated_at.isoformat()
        }
        
        redis_client.set(cache_key, payment_dict, expire=300)
        return payment_dict
    
    @staticmethod
    def get_all_payments(db: Session, order_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Payment]:
        """Получить список платежей с фильтрацией"""
        query = db.query(Payment)
        
        if order_id is not None:
            query = query.filter(Payment.order_id == order_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_payment(db: Session, payment_data: PaymentCreate) -> Payment:
        """
        Создать новый платеж с имитацией обработки
        
        Имитация: 30% шанс отказа
        """
        payment = Payment(**payment_data.model_dump())
        
        # Имитация обработки платежа (30% шанс отказа)
        if random.random() < 0.3:
            payment.status = PaymentStatus.FAILED.value
            print(f"💳 Payment FAILED for order {payment.order_id}")
        else:
            payment.status = PaymentStatus.COMPLETED.value
            print(f"✅ Payment COMPLETED for order {payment.order_id}")
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
    
    @staticmethod
    def update_payment(db: Session, payment_id: int, payment_data: PaymentUpdate) -> Optional[Payment]:
        """Обновить статус платежа"""
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            return None
        
        update_data = payment_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(payment, key, value)
        
        db.commit()
        db.refresh(payment)
        
        # Инвалидируем кэш
        redis_client.delete(f"payment:{payment_id}")
        print(f"🗑️  Cache invalidated for payment:{payment_id}")
        
        return payment
    
    @staticmethod
    def delete_payment(db: Session, payment_id: int) -> Optional[Payment]:
        """Удалить платеж"""
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            return None
        
        db.delete(payment)
        db.commit()
        
        redis_client.delete(f"payment:{payment_id}")
        print(f"🗑️  Cache invalidated for payment:{payment_id}")
        
        return payment


payment_service = PaymentService()
