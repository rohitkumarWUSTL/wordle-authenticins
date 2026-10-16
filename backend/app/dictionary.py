"""Dictionary helpers backed by generated text files.

Layout:

    app/data/words_{length}.txt

Each file has a single section:

    # answers
    <one word per line>

Answers are picked uniformly at random from the answer pool (matching
Wordle's behavior). Guess validation reads the raw TWL06 Scrabble word
list (``app/data/twl06.txt``) directly, so any Scrabble-legal word of the
right length is accepted as a guess. Files are generated on demand by
``scripts.generate_words`` if missing.
"""

from __future__ import annotations

import random
from functools import lru_cache
from pathlib import Path

from app.constants import MAX_WORD_LENGTH, MIN_WORD_LENGTH

DATA_DIR = Path(__file__).resolve().parent / "data"


def _words_path(length: int) -> Path:
    return DATA_DIR / f"words_{length}.txt"


def _scrabble_path() -> Path:
    return DATA_DIR / "twl06.txt"


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
def _load_words(length: int) -> tuple[str, ...]:
    path = ensure_words_txt(length)
    answers: list[str] = []
    section: list[str] | None = None
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line == "# answers":
                section = answers
                continue
            if section is not None:
                section.append(line)
    return tuple(answers)


@lru_cache(maxsize=None)
def _load_scrabble_words() -> frozenset[str]:
    """Load the raw TWL06 word list, lowercased.

    The file is all uppercase, so we lowercase on load to match the
    lowercased guesses the service passes in.
    """
    words: set[str] = set()
    with _scrabble_path().open("r", encoding="utf-8") as f:
        for line in f:
            word = line.strip().lower()
            if word.isalpha():
                words.add(word)
    return frozenset(words)


def seed_dictionary() -> None:
    """Ensure the words files exist and warm the in-memory caches.

    Called at startup so the first request for a given word length doesn't
    pay the cost of generating the file and parsing it.
    """
    for length in range(MIN_WORD_LENGTH, MAX_WORD_LENGTH + 1):
        ensure_words_txt(length)
        _load_words(length)
    _load_scrabble_words()


def is_valid_guess(word: str, length: int) -> bool:
    word = word.lower()
    if len(word) != length:
        return False
    return word in _load_scrabble_words()


def random_answer(length: int) -> str:
    answers = _load_words(length)
    if not answers:
        raise RuntimeError(f"No answers seeded for length {length}")
    return random.choice(answers)
