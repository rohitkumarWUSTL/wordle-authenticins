"""Generate the word list text files used to seed the dictionary.

Run as: python -m scripts.generate_words

Produces one file per word length under backend/app/data/:

    words_5.txt
    words_6.txt
    words_7.txt
    words_8.txt

Each file has the shape:

    # answers
    crane
    slate
    ...

    # guesses
    aahed
    aaron
    ...

Answers are the top ANSWER_COUNT words by zipf frequency for that length.
Guesses are the top GUESS_COUNT words by zipf frequency for that length
(a superset of answers).
"""

from __future__ import annotations

import os
from pathlib import Path

from wordfreq import iter_wordlist

from app.constants import MAX_WORD_LENGTH, MIN_WORD_LENGTH

ANSWER_COUNT = 1000
GUESS_COUNT = 25000

DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data"


def _collect_words() -> dict[int, dict[str, list[str]]]:
    # Bucket words by length as we stream the frequency-ordered wordlist.
    # iter_wordlist yields words in descending frequency order, so the first
    # N words we see for a given length are the top N by frequency.
    buckets: dict[int, list[str]] = {
        n: [] for n in range(MIN_WORD_LENGTH, MAX_WORD_LENGTH + 1)
    }
    max_needed = max(GUESS_COUNT, ANSWER_COUNT)

    for word in iter_wordlist("en"):
        if not word.isalpha():
            continue
        length = len(word)
        if length not in buckets:
            continue
        bucket = buckets[length]
        if len(bucket) >= max_needed:
            continue
        bucket.append(word)
        if all(
            len(buckets[n]) >= max_needed
            for n in range(MIN_WORD_LENGTH, MAX_WORD_LENGTH + 1)
        ):
            break

    result: dict[int, dict[str, list[str]]] = {}
    for length in range(MIN_WORD_LENGTH, MAX_WORD_LENGTH + 1):
        words = buckets[length]
        # iter_wordlist is already frequency-ordered, so slicing preserves order.
        answers = words[:ANSWER_COUNT]
        guesses = words[:GUESS_COUNT]
        result[length] = {"answers": answers, "guesses": guesses}
    return result


def _words_path(length: int, data_dir: Path = DATA_DIR) -> Path:
    return data_dir / f"words_{length}.txt"


def _write_words_file(
    path: Path, answers: list[str], guesses: list[str]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".txt.tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        f.write("# answers\n")
        for word in answers:
            f.write(f"{word}\n")
        f.write("\n# guesses\n")
        for word in guesses:
            f.write(f"{word}\n")
    os.replace(tmp_path, path)


def generate(data_dir: Path = DATA_DIR) -> Path:
    data = _collect_words()
    for length, entry in data.items():
        _write_words_file(
            _words_path(length, data_dir),
            entry["answers"],
            entry["guesses"],
        )
    return data_dir


if __name__ == "__main__":
    path = generate()
    print(f"Wrote word files to {path}")
