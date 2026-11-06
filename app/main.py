import logging
import time
from fastapi import Depends, FastAPI, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.orm import Session
import redis
from app.cache import cache_orders, get_cached_orders, get_redis, invalidate_orders
from app.config import settings
from app.database import Base, engine, get_db
from app.metrics import REQUEST_COUNT, REQUEST_LATENCY, metrics_response
from app.models import Order
from app.schemas import OrderCreate, OrderRead

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("orders-api")
app = FastAPI(title=settings.app_name, version="1.0.0", description="Production-oriented learning API for DevOps Project 01")


@app.on_event("startup")
def create_tables() -> None:
    # For this learning project only. Use Alembic migrations in a real production deployment.
    Base.metadata.create_all(bind=engine)


@app.middleware("http")
async def observe_requests(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - started
    REQUEST_COUNT.labels(request.method, request.url.path, str(response.status_code)).inc()
    REQUEST_LATENCY.labels(request.method, request.url.path).observe(elapsed)
    logger.info("request method=%s path=%s status=%s duration_ms=%.2f", request.method, request.url.path, response.status_code, elapsed * 1000)
    return response


@app.get("/health", tags=["operations"])
def health(db: Session = Depends(get_db), cache: redis.Redis = Depends(get_redis)):
    checks = {}
    try:
        db.execute(text("SELECT 1"))
        checks["postgresql"] = "ok"
    except Exception:
        checks["postgresql"] = "unavailable"
    try:
        cache.ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "unavailable"
    healthy = all(value == "ok" for value in checks.values())
    return {"status": "ok" if healthy else "degraded", "checks": checks}


@app.get("/metrics", include_in_schema=False, tags=["operations"])
def metrics():
    return metrics_response()


@app.get("/orders", response_model=list[OrderRead], tags=["orders"])
def list_orders(db: Session = Depends(get_db), cache: redis.Redis = Depends(get_redis)):
    try:
        cached = get_cached_orders(cache)
        if cached is not None:
            return cached
    except redis.RedisError:
        logger.warning("Redis read failed; falling back to PostgreSQL")
    orders = db.query(Order).order_by(Order.id).all()
    result = [OrderRead.model_validate(order).model_dump(mode="json") for order in orders]
    try:
        cache_orders(cache, result)
    except redis.RedisError:
        logger.warning("Redis write failed; response served without cache")
    return result


@app.post("/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED, tags=["orders"])
def create_order(payload: OrderCreate, db: Session = Depends(get_db), cache: redis.Redis = Depends(get_redis)):
    order = Order(**payload.model_dump())
    db.add(order)
    db.commit()
    db.refresh(order)
    try:
        invalidate_orders(cache)
    except redis.RedisError:
        logger.warning("Redis invalidation failed after order creation")
    logger.info("created order_id=%s", order.id)
    return order
