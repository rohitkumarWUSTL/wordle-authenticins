"""Dictionary helpers backed by Redis.

Redis layout:

    dict:answer:{length}   LIST  expanded by zipf weight (LRANDMEMBER picks target)
    dict:guess:{length}    SET   valid guesses (SISMEMBER validates)

The JSON source of truth lives at app/data/words.json and is generated on
demand by scripts.generate_words if missing.
"""

from __future__ import annotations

import json
from pathlib import Path

import redis.asyncio as redis
from wordfreq import zipf_frequency

from app.constants import MAX_WORD_LENGTH, MIN_WORD_LENGTH

DATA_PATH = Path(__file__).resolve().parent / "data" / "words.json"


def _answer_key(length: int) -> str:
    return f"dict:answer:{length}"


def _guess_key(length: int) -> str:
    return f"dict:guess:{length}"


def _weight(word: str) -> int:
    # Linear in zipf: a zipf-7 word appears 6x, a zipf-2 word appears 1x.
    return max(1, round(zipf_frequency(word, "en") - 1))


def ensure_words_json(path: Path = DATA_PATH) -> Path:
    """Generate the words JSON if it doesn't already exist."""
    if path.exists():
        return path
    # Imported lazily so the runtime doesn't need wordfreq unless generating.
    from scripts.generate_words import generate

    return generate(path)


def _load_words(path: Path = DATA_PATH) -> dict[str, dict[str, list[str]]]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


async def seed_dictionary(
    client: redis.Redis, path: Path = DATA_PATH
) -> None:
    """Seed Redis from the words JSON, per-partition, only if missing."""
    data = _load_words(path)

    for length in range(MIN_WORD_LENGTH, MAX_WORD_LENGTH+1):
        entry = data[str(length)]

        answer_key = _answer_key(length)
        if not await client.exists(answer_key):
            expanded: list[str] = []
            for word in entry["answers"]:
                expanded.extend([word] * _weight(word))
            if expanded:
                # LPUSH in reverse so LRANDMEMBER sees a stable order.
                await client.rpush(answer_key, *reversed(expanded))

        guess_key = _guess_key(length)
        if not await client.exists(guess_key):
            guesses = entry["guesses"]
            if guesses:
                await client.sadd(guess_key, *guesses)


async def is_valid_guess(client: redis.Redis, word: str, length: int) -> bool:
    return bool(await client.sismember(_guess_key(length), word.lower()))


async def random_answer(client: redis.Redis, length: int) -> str:
    word = await client.lrandmember(_answer_key(length))
    if word is None:
        raise RuntimeError(f"No answers seeded for length {length}")
    return word
