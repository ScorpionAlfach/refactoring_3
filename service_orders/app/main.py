from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import init_db
from .routes import orders
from .redis_client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events для FastAPI"""
    # Startup
    print("🚀 Initializing Orders Service...")
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
    print("👋 Shutting down Orders Service...")


app = FastAPI(
    title="Orders Service",
    description="Микросервис для управления заказами",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "Orders Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "OK",
        "service": "Orders Service",
        "redis": redis_client.ping()
    }
