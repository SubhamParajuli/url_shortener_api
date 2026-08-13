"""
quick manual script to check redis connection is working fine or not.
not a real pytest test (no assert), just set a key n print it back.
"""
from app.redis_client import redis_client

redis_client.set(
    'test_key',
    "hello redis"
)

value=redis_client.get("test_key")
print(value)
