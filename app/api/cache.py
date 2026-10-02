"""Cache opcional con Redis.

Si REDIS_URL no está definida, la app funciona igual pero sin cache.
Si Redis se cae, la app NO se cae: solo pierde el cache (degradación elegante).
"""

import logging
import os

import redis

log = logging.getLogger("tasks-api.cache")
_client: redis.Redis | None = None


def get_client() -> redis.Redis | None:
    global _client
    url = os.getenv("REDIS_URL")
    if not url:
        return None
    if _client is None:
        _client = redis.Redis.from_url(url, socket_timeout=1, decode_responses=True)
    return _client


def get(key: str) -> str | None:
    client = get_client()
    if client is None:
        return None
    try:
        return client.get(key)
    except redis.RedisError as exc:
        log.warning("redis get falló: %s", exc)
        return None


def set(key: str, value: str, ttl: int = 30) -> None:
    client = get_client()
    if client is None:
        return
    try:
        client.set(key, value, ex=ttl)
    except redis.RedisError as exc:
        log.warning("redis set falló: %s", exc)


def delete(key: str) -> None:
    client = get_client()
    if client is None:
        return
    try:
        client.delete(key)
    except redis.RedisError as exc:
        log.warning("redis delete falló: %s", exc)


def ping() -> bool | None:
    """True/False si hay Redis configurado, None si no se usa."""
    client = get_client()
    if client is None:
        return None
    try:
        return bool(client.ping())
    except redis.RedisError:
        return False
