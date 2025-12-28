from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@db_users:5432/users_db"
)

# Создаём движок SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)

# Создаём фабрику сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """Dependency для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Инициализация базы данных (создание таблиц)"""
    Base.metadata.create_all(bind=engine)
