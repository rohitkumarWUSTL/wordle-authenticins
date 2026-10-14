"""Generate the word list JSON used to seed Redis.

Run as: python -m scripts.generate_words

Produces backend/app/data/words.json with the shape:

    {
      "5": {"answers": [...], "guesses": [...]},
      "6": {"answers": [...], "guesses": [...]},
      "7": {"answers": [...], "guesses": [...]},
      "8": {"answers": [...], "guesses": [...]}
    }

Answers are the top ANSWER_COUNT words by zipf frequency for each length.
Guesses are the top GUESS_COUNT words by zipf frequency for each length
(a superset of answers).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from wordfreq import iter_wordlist, zipf_frequency

WORD_LENGTHS = (5, 6, 7, 8)
ANSWER_COUNT = 1000
GUESS_COUNT = 25000

DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data"
OUTPUT_PATH = DATA_DIR / "words.json"


def _collect_words() -> dict[str, dict[str, list[str]]]:
    # Bucket words by length as we stream the frequency-ordered wordlist.
    # iter_wordlist yields words in descending frequency order, so the first
    # N words we see for a given length are the top N by frequency.
    buckets: dict[int, list[str]] = {n: [] for n in WORD_LENGTHS}
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
        if all(len(buckets[n]) >= max_needed for n in WORD_LENGTHS):
            break

    result: dict[str, dict[str, list[str]]] = {}
    for length in WORD_LENGTHS:
        words = buckets[length]
        # iter_wordlist is already frequency-ordered, so slicing preserves order.
        answers = words[:ANSWER_COUNT]
        guesses = words[:GUESS_COUNT]
        result[str(length)] = {"answers": answers, "guesses": guesses}
    return result


def generate(output_path: Path = OUTPUT_PATH) -> Path:
    data = _collect_words()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(".json.tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, output_path)
    return output_path


if __name__ == "__main__":
    path = generate()
    print(f"Wrote {path}")
