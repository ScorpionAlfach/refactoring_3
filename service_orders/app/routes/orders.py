from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..schemas import OrderCreate, OrderUpdate, OrderResponse
from ..services.order_service import order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=List[OrderResponse])
def get_orders(
    userId: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список заказов с фильтрацией по userId"""
    orders = order_service.get_all_orders(db, user_id=userId, skip=skip, limit=limit)
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Получить заказ по ID (с кэшированием)"""
    order = order_service.get_order_by_id(db, order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """Создать новый заказ"""
    order = order_service.create_order(db, order_data)
    return order


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db)
):
    """Обновить заказ"""
    order = order_service.update_order(db, order_id, order_data)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Удалить заказ"""
    order = order_service.delete_order(db, order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return {
        "message": "Order deleted",
        "deletedOrder": {
            "id": order.id,
            "userId": order.userId,
            "product": order.product,
            "quantity": order.quantity
        }
    }


@router.get("/status")
def status():
    """Status endpoint"""
    return {"status": "Orders service is running"}


@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "OK",
        "service": "Orders Service"
    }
