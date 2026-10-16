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

Answers are the top ANSWER_COUNT words by zipf frequency for that length
that pass the answer filter (frequency floor, no proper nouns, no plurals).
Guesses are the top GUESS_COUNT words by zipf frequency for that length
that pass the guess filter (lower frequency floor, no proper nouns).
Answers are always a subset of guesses.
"""

from __future__ import annotations

import os
from pathlib import Path

from wordfreq import iter_wordlist, zipf_frequency

from app.constants import MAX_WORD_LENGTH, MIN_WORD_LENGTH

# Frequency floors. Answers are held to a higher bar than guesses so the
# answer pool feels like Wordle's curated list, while guesses stay permissive
# enough that players rarely hit "not a valid word".
MIN_ZIPF_ANSWERS = 3.5
MIN_ZIPF_GUESSES = 2.5

ANSWER_COUNT = 2500
GUESS_COUNT = 15000

DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data"


def _is_likely_proper_noun(word: str) -> bool:
    """Heuristic: a word is likely a proper noun if its capitalized form is
    significantly more frequent than its lowercase form (e.g. "jeremy")."""
    lower = zipf_frequency(word, "en")
    upper = zipf_frequency(word.capitalize(), "en")
    return upper > lower + 1.0


def _is_plural(word: str, all_words: set[str]) -> bool:
    """Heuristic: a word is likely a plural if it ends in "s" and its
    singular form is also a known word. Excludes common non-plural "s"
    endings (glass, cactus, basis)."""
    if not word.endswith("s"):
        return False
    if word.endswith(("ss", "us", "is")):
        return False
    return word[:-1] in all_words


def _collect_words() -> dict[int, dict[str, list[str]]]:
    # First pass: collect all candidates that pass the guess filter.
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
        if zipf_frequency(word, "en") < MIN_ZIPF_GUESSES:
            continue
        if _is_likely_proper_noun(word):
            continue
        bucket.append(word)
        if all(
            len(buckets[n]) >= max_needed
            for n in range(MIN_WORD_LENGTH, MAX_WORD_LENGTH + 1)
        ):
            break

    # Second pass: derive answers from the guess pool.
    result: dict[int, dict[str, list[str]]] = {}
    for length in range(MIN_WORD_LENGTH, MAX_WORD_LENGTH + 1):
        words = buckets[length]
        all_words = set(words)
        answers = [
            w
            for w in words
            if zipf_frequency(w, "en") >= MIN_ZIPF_ANSWERS
            and not _is_plural(w, all_words)
        ][:ANSWER_COUNT]
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
