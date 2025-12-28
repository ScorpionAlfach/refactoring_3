from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..schemas import PaymentCreate, PaymentUpdate, PaymentResponse
from ..services.payment_service import payment_service

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("", response_model=List[PaymentResponse])
def get_payments(
    order_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список платежей с фильтрацией по order_id"""
    payments = payment_service.get_all_payments(db, order_id=order_id, skip=skip, limit=limit)
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    """Получить платеж по ID (с кэшированием)"""
    payment = payment_service.get_payment_by_id(db, payment_id)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment_data: PaymentCreate, db: Session = Depends(get_db)):
    """
    Создать новый платеж с имитацией обработки
    
    Имитация: 30% шанс отказа (статус failed)
    """
    payment = payment_service.create_payment(db, payment_data)
    return payment


@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db)
):
    """Обновить статус платежа"""
    payment = payment_service.update_payment(db, payment_id, payment_data)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment


@router.delete("/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    """Удалить платеж"""
    payment = payment_service.delete_payment(db, payment_id)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return {
        "message": "Payment deleted",
        "deletedPayment": {
            "id": payment.id,
            "order_id": payment.order_id,
            "amount": payment.amount,
            "status": payment.status
        }
    }


@router.get("/status")
def status_check():
    """Status endpoint"""
    return {"status": "Payments service is running"}


@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "OK",
        "service": "Payments Service"
    }
