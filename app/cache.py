import json
import redis
from app.config import settings


def get_redis() -> redis.Redis:
    return redis.Redis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=1)


def get_cached_orders(client: redis.Redis):
    payload = client.get("orders:all")
    return json.loads(payload) if payload else None


def cache_orders(client: redis.Redis, orders: list[dict]) -> None:
    client.setex("orders:all", settings.cache_ttl_seconds, json.dumps(orders, default=str))


def invalidate_orders(client: redis.Redis) -> None:
    client.delete("orders:all")
