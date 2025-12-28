from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..schemas import UserCreate, UserUpdate, UserResponse
from ..services.user_service import user_service
from ..models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список всех пользователей"""
    users = user_service.get_all_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Получить пользователя по ID (с кэшированием)"""
    user = user_service.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Создать нового пользователя"""
    # Проверка на существующий email
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = user_service.create_user(db, user_data)
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """Обновить пользователя"""
    user = user_service.update_user(db, user_id, user_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Удалить пользователя"""
    user = user_service.delete_user(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "message": "User deleted",
        "deletedUser": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }


@router.get("/status")
def status():
    """Status endpoint"""
    return {"status": "Users service is running"}


@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "OK",
        "service": "Users Service"
    }
