"""Generate the word list text files used to seed the dictionary.

Run as: python -m scripts.generate_words

Produces one file per word length under backend/app/data/:

    words_5.txt
    words_6.txt
    words_7.txt
    words_8.txt

Each file has the shape:

    # answers
    about
    their
    ...

    # guesses
    about
    their
    ...

The source of truth is a TWL06 Scrabble word list (see SOURCE_PATH). TWL06
already excludes proper nouns, so no name filtering is needed. Answers are
the top ANSWER_COUNT words by zipf frequency for that length that pass the
answer filter (frequency floor, and not a plural). The ``# guesses`` section
is retained for backwards compatibility with the file format, but guess
validation now reads twl06.txt directly (see app/dictionary.py), so the
contents of that section are not used at runtime.
"""

from __future__ import annotations

import os
from pathlib import Path

from wordfreq import zipf_frequency

from app.constants import MAX_WORD_LENGTH, MIN_WORD_LENGTH

# Frequency floor for answers. Answers are held to a higher bar than guesses
# so the answer pool feels like Wordle's curated list.
MIN_ZIPF_ANSWERS = 3.5

ANSWER_COUNT = 2500

DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data"
SOURCE_PATH = DATA_DIR / "twl06.txt"


def _load_source_words(
    path: Path = SOURCE_PATH, *, filter_by_length: bool = True
) -> set[str]:
    """Load the TWL06 word list, lowercased, keeping only alphabetic words.

    When ``filter_by_length`` is true (the default), words outside the
    supported length range are dropped. The plural check needs the
    unfiltered list so it can see short singulars like 'frog' that aren't
    valid answers themselves.
    """
    words: set[str] = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            word = line.strip().lower()
            if not word.isalpha():
                continue
            if filter_by_length and not (
                MIN_WORD_LENGTH <= len(word) <= MAX_WORD_LENGTH
            ):
                continue
            words.add(word)
    return words


def _is_plural(word: str, source: set[str]) -> bool:
    """Heuristic: a word is a plural if stripping a plural suffix yields
    another word in the source list.

    Used to keep plurals out of the answer pool (Wordle never uses them as
    answers) while still allowing them as guesses. Irregular plurals
    (``mice``, ``geese``) are not detected; they are rare at the supported
    word lengths and mostly fall below the answer frequency floor.

    ``source`` should be the *unfiltered* word list, so that plurals whose
    singular is shorter than the minimum word length (``frogs`` -> ``frog``)
    are still detected.
    """
    if word.endswith("ies") and word[:-3] + "y" in source:
        return True
    if word.endswith("ves") and word[:-3] + "f" in source:
        return True
    if word.endswith("ves") and word[:-3] + "fe" in source:
        return True
    if word.endswith("es") and word[:-2] in source:
        return True
    if word.endswith("s") and word[:-1] in source:
        return True
    return False


def _collect_words(
    source: set[str], all_words: set[str]
) -> dict[int, dict[str, list[str]]]:
    # Bucket the source words by length, then sort each bucket by descending
    # zipf frequency so the most common words come first.
    buckets: dict[int, list[str]] = {
        n: [] for n in range(MIN_WORD_LENGTH, MAX_WORD_LENGTH + 1)
    }
    for word in source:
        buckets[len(word)].append(word)

    result: dict[int, dict[str, list[str]]] = {}
    for length in range(MIN_WORD_LENGTH, MAX_WORD_LENGTH + 1):
        words = sorted(
            buckets[length],
            key=lambda w: zipf_frequency(w, "en"),
            reverse=True,
        )
        answers = [
            w
            for w in words
            if zipf_frequency(w, "en") >= MIN_ZIPF_ANSWERS
            and not _is_plural(w, all_words)
        ][:ANSWER_COUNT]
        # The guesses section is no longer used for validation (see
        # app/dictionary.py), but we keep writing it so the file format is
        # unchanged. It mirrors the full length-filtered word list.
        guesses = words
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
    all_words = _load_source_words(
        data_dir / "twl06.txt", filter_by_length=False
    )
    source = {
        w
        for w in all_words
        if MIN_WORD_LENGTH <= len(w) <= MAX_WORD_LENGTH
    }
    data = _collect_words(source, all_words)
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
