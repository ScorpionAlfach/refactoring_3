from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import init_db
from .routes import payments
from .redis_client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events для FastAPI"""
    print("🚀 Initializing Payments Service...")
    print("📊 Initializing database...")
    init_db()
    print("✅ Database initialized")
    
    if redis_client.ping():
        print("✅ Redis connected - caching enabled")
    else:
        print("⚠️  Redis not available - caching disabled")
    
    yield
    
    print("👋 Shutting down Payments Service...")


app = FastAPI(
    title="Payments Service",
    description="Микросервис для обработки платежей",
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

app.include_router(payments.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "Payments Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "OK",
        "service": "Payments Service",
        "redis": redis_client.ping()
    }
