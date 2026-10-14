from __future__ import annotations

import redis.asyncio as redis

from app import dictionary


class DictionaryRepository:
    def __init__(self, client: redis.Redis) -> None:
        self._client = client

    async def is_valid(self, word: str, length: int) -> bool:
        return await dictionary.is_valid_guess(self._client, word, length)

    async def random_answer(self, length: int) -> str:
        try:
            return await dictionary.random_answer(self._client, length)
        except (redis.RedisError, RuntimeError):
            return dictionary.random_answer_fallback(length)
