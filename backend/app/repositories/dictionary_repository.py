from __future__ import annotations

import redis.asyncio as redis

from app import dictionary


class DictionaryRepository:
    def __init__(self, client: redis.Redis) -> None:
        self._client = client

    async def is_valid(self, word: str, length: int) -> bool:
        raise NotImplementedError

    async def random_answer(self, length: int) -> str:
        raise NotImplementedError
