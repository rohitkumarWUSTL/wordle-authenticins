from __future__ import annotations

from app.repositories.dictionary_repository import DictionaryRepository


async def test_is_valid_hit(dictionary_repo: DictionaryRepository) -> None:
    await dictionary_repo._client.sadd("words:guess:5", "apple")
    assert await dictionary_repo.is_valid("apple", 5) is True


async def test_is_valid_miss(dictionary_repo: DictionaryRepository) -> None:
    assert await dictionary_repo.is_valid("zzzzz", 5) is False


async def test_random_answer(dictionary_repo: DictionaryRepository) -> None:
    await dictionary_repo._client.sadd("words:answer:5", "apple")
    word = await dictionary_repo.random_answer(5)
    assert word == "apple"
    assert len(word) == 5
