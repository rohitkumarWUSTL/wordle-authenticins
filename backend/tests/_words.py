"""Shared helpers for seeding the txt-backed dictionary in tests.

The dictionary reads from ``dictionary.DATA_DIR`` (monkeypatched to a
``tmp_path`` by the ``data_dir`` fixture in ``conftest.py``). These helpers
write into that directory and clear the loader caches so the next read picks
up the new contents.
"""

from __future__ import annotations

from pathlib import Path

from app import dictionary


def read_words_file(path: Path) -> tuple[list[str], list[str]]:
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


def write_words_file(
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


def _clear_caches() -> None:
    dictionary._load_words.cache_clear()
    dictionary._weighted_answers.cache_clear()


def seed_answer(word: str) -> None:
    data_dir = dictionary.DATA_DIR
    length = len(word)
    path = data_dir / f"words_{length}.txt"
    answers: list[str] = []
    guesses: list[str] = []
    if path.exists():
        answers, guesses = read_words_file(path)
    answers.append(word)
    write_words_file(data_dir, length, answers, guesses)
    _clear_caches()


def seed_guess(word: str) -> None:
    data_dir = dictionary.DATA_DIR
    length = len(word)
    path = data_dir / f"words_{length}.txt"
    answers: list[str] = []
    guesses: list[str] = []
    if path.exists():
        answers, guesses = read_words_file(path)
    guesses.append(word)
    write_words_file(data_dir, length, answers, guesses)
    _clear_caches()


def seed_empty(length: int) -> None:
    write_words_file(dictionary.DATA_DIR, length, [], [])
    _clear_caches()
