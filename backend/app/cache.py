from collections.abc import AsyncGenerator

import redis.asyncio as redis

from app.config import get_settings

settings = get_settings()

redis_client: redis.Redis = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    yield redis_client
