from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import init_db
from .routes import users
from .redis_client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events для FastAPI"""
    # Startup
    print("🚀 Initializing Users Service...")
    print("📊 Initializing database...")
    init_db()
    print("✅ Database initialized")
    
    # Проверяем Redis
    if redis_client.ping():
        print("✅ Redis connected - caching enabled")
    else:
        print("⚠️  Redis not available - caching disabled")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Users Service...")


# Создаём FastAPI приложение
app = FastAPI(
    title="Users Service",
    description="Микросервис для управления пользователями",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(users.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "Users Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "OK",
        "service": "Users Service",
        "redis": redis_client.ping()
    }
