"""Dictionary helpers backed by generated text files.

Layout:

    app/data/words_{length}.txt

Each file has two sections:

    # answers
    <one word per line>

    # guesses
    <one word per line>

Answers are picked uniformly at random from the answer pool (matching
Wordle's behavior); guesses are validated by set membership. Files are
generated on demand by ``scripts.generate_words`` if missing.
"""

from __future__ import annotations

import random
from functools import lru_cache
from pathlib import Path

from app.constants import MAX_WORD_LENGTH, MIN_WORD_LENGTH

DATA_DIR = Path(__file__).resolve().parent / "data"


def _words_path(length: int) -> Path:
    return DATA_DIR / f"words_{length}.txt"


def ensure_words_txt(length: int) -> Path:
    """Generate the words file for ``length`` if it doesn't already exist."""
    path = _words_path(length)
    if path.exists():
        return path
    # Imported lazily so the runtime doesn't need wordfreq unless generating.
    from scripts.generate_words import generate

    generate(DATA_DIR)
    return path


@lru_cache(maxsize=None)
def _load_words(length: int) -> tuple[tuple[str, ...], frozenset[str]]:
    path = ensure_words_txt(length)
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
    return tuple(answers), frozenset(guesses)


def seed_dictionary() -> None:
    """Ensure the words files exist and warm the in-memory caches.

    Called at startup so the first request for a given word length doesn't
    pay the cost of generating the file and parsing it.
    """
    for length in range(MIN_WORD_LENGTH, MAX_WORD_LENGTH + 1):
        ensure_words_txt(length)
        _load_words(length)


def is_valid_guess(word: str, length: int) -> bool:
    _, guesses = _load_words(length)
    return word.lower() in guesses


def random_answer(length: int) -> str:
    answers, _ = _load_words(length)
    if not answers:
        raise RuntimeError(f"No answers seeded for length {length}")
    return random.choice(answers)
