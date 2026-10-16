from __future__ import annotations

from app.repositories.dictionary_repository import DictionaryRepository
from tests._words import seed_answer, seed_empty, seed_scrabble


async def test_is_valid_hit(dictionary_repo: DictionaryRepository) -> None:
    seed_scrabble(["apple"])
    assert await dictionary_repo.is_valid("apple", 5) is True


async def test_is_valid_miss(dictionary_repo: DictionaryRepository) -> None:
    seed_empty(5)
    assert await dictionary_repo.is_valid("zzzzz", 5) is False


async def test_random_answer(dictionary_repo: DictionaryRepository) -> None:
    seed_answer("apple")
    word = await dictionary_repo.random_answer(5)
    assert word == "apple"
    assert len(word) == 5
