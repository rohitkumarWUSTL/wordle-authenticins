"""Tests for the dictionary module.

Guess validation reads ``twl06.txt`` directly (uppercased on disk), while
answers come from the generated ``words_{length}.txt`` files. These tests
pin both behaviors, plus the case-insensitivity of guess validation.
"""

from __future__ import annotations

import pytest

from app import dictionary
from tests._words import seed_answer, seed_empty, seed_scrabble


def test_is_valid_guess_accepts_scrabble_word(data_dir) -> None:
    seed_scrabble(["apple", "crane"])
    assert dictionary.is_valid_guess("apple", 5) is True


def test_is_valid_guess_rejects_word_not_in_scrabble(data_dir) -> None:
    seed_scrabble(["apple", "crane"])
    assert dictionary.is_valid_guess("zzzzz", 5) is False


def test_is_valid_guess_is_case_insensitive(data_dir) -> None:
    seed_scrabble(["apple"])
    assert dictionary.is_valid_guess("APPLE", 5) is True
    assert dictionary.is_valid_guess("Apple", 5) is True


def test_is_valid_guess_rejects_wrong_length(data_dir) -> None:
    seed_scrabble(["apple"])
    # "apple" is 5 letters; asking about length 6 must not match.
    assert dictionary.is_valid_guess("apple", 6) is False


def test_is_valid_guess_ignores_guesses_section(data_dir) -> None:
    """A word in the generated guesses section is not valid unless it's
    also in twl06.txt."""
    seed_empty(5)
    # seed_empty writes an empty words_5.txt; the guesses section is empty.
    # Now write a twl06.txt that does NOT contain "apple".
    seed_scrabble(["crane"])
    assert dictionary.is_valid_guess("apple", 5) is False


def test_is_valid_guess_reads_from_scrabble_not_answers(data_dir) -> None:
    """A word in the answers section is not valid unless it's also in
    twl06.txt."""
    seed_answer("apple")
    seed_scrabble(["crane"])
    assert dictionary.is_valid_guess("apple", 5) is False


def test_random_answer_returns_seeded_answer(data_dir) -> None:
    seed_answer("apple")
    assert dictionary.random_answer(5) == "apple"


def test_random_answer_raises_when_empty(data_dir) -> None:
    seed_empty(5)
    with pytest.raises(RuntimeError, match="No answers seeded"):
        dictionary.random_answer(5)
