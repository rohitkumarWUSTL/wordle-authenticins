from __future__ import annotations

from app import dictionary


class DictionaryRepository:
    async def is_valid(self, word: str, length: int) -> bool:
        return dictionary.is_valid_guess(word, length)

    async def random_answer(self, length: int) -> str:
        return dictionary.random_answer(length)
