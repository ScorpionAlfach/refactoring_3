from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional

app = FastAPI(title="API Gateway", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Адреса сервисов
USERS_SERVICE_URL = "http://service_users:8000"
ORDERS_SERVICE_URL = "http://service_orders:8000"
PAYMENTS_SERVICE_URL = "http://service_payments:8000"

# Circuit Breaker configuration
class CircuitBreakerConfig:
    def __init__(self):
        self.failure_threshold = 5
        self.timeout_duration = 30
        self.request_timeout = 3.0

class CircuitBreaker:
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"
        
    def is_open(self) -> bool:
        if self.state == "OPEN":
            if self.last_failure_time and \
               datetime.now() - self.last_failure_time > timedelta(seconds=self.config.timeout_duration):
                self.state = "HALF_OPEN"
                print(f"🔄 {self.name} circuit breaker half-open")
                return False
            return True
        return False
    
    def record_success(self):
        self.failure_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            print(f"✅ {self.name} circuit breaker closed")
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.config.failure_threshold:
            self.state = "OPEN"
            print(f"🔴 {self.name} circuit breaker opened")
    
    async def call(self, func, *args, **kwargs):
        if self.is_open():
            raise HTTPException(
                status_code=503,
                detail=f"{self.name} service temporarily unavailable"
            )
        
        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise e

# Создаем circuit breakers
config = CircuitBreakerConfig()
users_circuit = CircuitBreaker("Users", config)
orders_circuit = CircuitBreaker("Orders", config)
payments_circuit = CircuitBreaker("Payments", config)

# HTTP клиент
async def make_request(url: str, method: str = "GET", data: dict = None):
    async with httpx.AsyncClient(timeout=3.0) as client:
        if method == "GET":
            response = await client.get(url)
        elif method == "POST":
            response = await client.post(url, json=data)
        elif method == "PUT":
            response = await client.put(url, json=data)
        elif method == "DELETE":
            response = await client.delete(url)
        
        if response.status_code == 404:
            return response.json()
        response.raise_for_status()
        return response.json()

# ============= USERS ENDPOINTS =============

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    try:
        result = await users_circuit.call(
            make_request,
            f"{USERS_SERVICE_URL}/users/{user_id}"
        )
        if isinstance(result, dict) and "detail" in result:
            raise HTTPException(status_code=404, detail=result["detail"])
        return result
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/users")
async def create_user(request: Request):
    try:
        data = await request.json()
        result = await users_circuit.call(
            make_request,
            f"{USERS_SERVICE_URL}/users",
            method="POST",
            data=data
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error creating user: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/users")
async def get_users():
    try:
        result = await users_circuit.call(
            make_request,
            f"{USERS_SERVICE_URL}/users"
        )
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    try:
        result = await users_circuit.call(
            make_request,
            f"{USERS_SERVICE_URL}/users/{user_id}",
            method="DELETE"
        )
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/users/{user_id}")
async def update_user(user_id: int, request: Request):
    try:
        data = await request.json()
        result = await users_circuit.call(
            make_request,
            f"{USERS_SERVICE_URL}/users/{user_id}",
            method="PUT",
            data=data
        )
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

# ============= ORDERS ENDPOINTS =============

@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    try:
        result = await orders_circuit.call(
            make_request,
            f"{ORDERS_SERVICE_URL}/orders/{order_id}"
        )
        if isinstance(result, dict) and "detail" in result:
            raise HTTPException(status_code=404, detail=result["detail"])
        return result
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/orders")
async def create_order(request: Request):
    try:
        data = await request.json()
        result = await orders_circuit.call(
            make_request,
            f"{ORDERS_SERVICE_URL}/orders",
            method="POST",
            data=data
        )
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/orders")
async def get_orders():
    try:
        result = await orders_circuit.call(
            make_request,
            f"{ORDERS_SERVICE_URL}/orders"
        )
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/orders/{order_id}")
async def delete_order(order_id: int):
    try:
        result = await orders_circuit.call(
            make_request,
            f"{ORDERS_SERVICE_URL}/orders/{order_id}",
            method="DELETE"
        )
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/orders/{order_id}")
async def update_order(order_id: int, request: Request):
    try:
        data = await request.json()
        result = await orders_circuit.call(
            make_request,
            f"{ORDERS_SERVICE_URL}/orders/{order_id}",
            method="PUT",
            data=data
        )
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

# ============= PAYMENTS ENDPOINTS =============

@app.get("/payments/{payment_id}")
async def get_payment(payment_id: int):
    try:
        result = await payments_circuit.call(
            make_request,
            f"{PAYMENTS_SERVICE_URL}/payments/{payment_id}"
        )
        if isinstance(result, dict) and "detail" in result:
            raise HTTPException(status_code=404, detail=result["detail"])
        return result
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/payments")
async def create_payment(request: Request):
    try:
        data = await request.json()
        result = await payments_circuit.call(
            make_request,
            f"{PAYMENTS_SERVICE_URL}/payments",
            method="POST",
            data=data
        )
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/payments")
async def get_payments():
    try:
        result = await payments_circuit.call(
            make_request,
            f"{PAYMENTS_SERVICE_URL}/payments"
        )
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/payments/{payment_id}")
async def delete_payment(payment_id: int):
    try:
        result = await payments_circuit.call(
            make_request,
            f"{PAYMENTS_SERVICE_URL}/payments/{payment_id}",
            method="DELETE"
        )
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/payments/{payment_id}")
async def update_payment(payment_id: int, request: Request):
    try:
        data = await request.json()
        result = await payments_circuit.call(
            make_request,
            f"{PAYMENTS_SERVICE_URL}/payments/{payment_id}",
            method="PUT",
            data=data
        )
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

# ============= API AGGREGATION =============

@app.get("/users/{user_id}/details")
async def get_user_details(user_id: int):
    """API Aggregation: Получить пользователя с его заказами"""
    try:
        user_task = users_circuit.call(
            make_request,
            f"{USERS_SERVICE_URL}/users/{user_id}"
        )
        orders_task = orders_circuit.call(
            make_request,
            f"{ORDERS_SERVICE_URL}/orders"
        )
        
        user, all_orders = await asyncio.gather(user_task, orders_task)
        
        if isinstance(user, dict) and "detail" in user:
            raise HTTPException(status_code=404, detail=user["detail"])
        
        user_orders = [order for order in all_orders if order.get("userId") == user_id]
        
        return {
            "user": user,
            "orders": user_orders
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

# ============= HEALTH & STATUS =============

@app.get("/health")
async def health():
    return {
        "status": "API Gateway is running",
        "circuits": {
            "users": {
                "status": users_circuit.state,
                "failure_count": users_circuit.failure_count
            },
            "orders": {
                "status": orders_circuit.state,
                "failure_count": orders_circuit.failure_count
            },
            "payments": {
                "status": payments_circuit.state,
                "failure_count": payments_circuit.failure_count
            }
        }
    }

@app.get("/status")
async def status():
    return {"status": "API Gateway is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
