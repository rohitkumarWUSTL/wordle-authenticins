from __future__ import annotations

from pathlib import Path

from app import dictionary
from app.repositories.dictionary_repository import DictionaryRepository


def _read_words_file(path: Path) -> tuple[list[str], list[str]]:
    answers: list[str] = []
    guesses: list[str] = []
    section: list[str] | None = None
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line == "# answers":
                section = answers
                continue
            if line == "# guesses":
                section = guesses
                continue
            if section is not None:
                section.append(line)
    return answers, guesses


def _write_words_file(
    data_dir: Path, length: int, answers: list[str], guesses: list[str]
) -> None:
    path = data_dir / f"words_{length}.txt"
    with path.open("w", encoding="utf-8") as f:
        f.write("# answers\n")
        for word in answers:
            f.write(f"{word}\n")
        f.write("\n# guesses\n")
        for word in guesses:
            f.write(f"{word}\n")


def _seed_answer(word: str) -> None:
    data_dir = dictionary.DATA_DIR
    length = len(word)
    path = data_dir / f"words_{length}.txt"
    answers: list[str] = []
    guesses: list[str] = []
    if path.exists():
        answers, guesses = _read_words_file(path)
    answers.append(word)
    _write_words_file(data_dir, length, answers, guesses)
    dictionary._load_words.cache_clear()
    dictionary._weighted_answers.cache_clear()


def _seed_guess(word: str) -> None:
    data_dir = dictionary.DATA_DIR
    length = len(word)
    path = data_dir / f"words_{length}.txt"
    answers: list[str] = []
    guesses: list[str] = []
    if path.exists():
        answers, guesses = _read_words_file(path)
    guesses.append(word)
    _write_words_file(data_dir, length, answers, guesses)
    dictionary._load_words.cache_clear()
    dictionary._weighted_answers.cache_clear()


async def test_is_valid_hit(dictionary_repo: DictionaryRepository) -> None:
    _seed_guess("apple")
    assert await dictionary_repo.is_valid("apple", 5) is True


async def test_is_valid_miss(dictionary_repo: DictionaryRepository) -> None:
    assert await dictionary_repo.is_valid("zzzzz", 5) is False


async def test_random_answer(dictionary_repo: DictionaryRepository) -> None:
    _seed_answer("apple")
    word = await dictionary_repo.random_answer(5)
    assert word == "apple"
    assert len(word) == 5
