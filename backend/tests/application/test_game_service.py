from __future__ import annotations

from pathlib import Path

import pytest

from app import dictionary
from app.application.game_service import GameService
from app.models.errors import (
    GameAlreadyFinished,
    GameNotFound,
    InvalidGuess,
)
from app.models.game import GameStatus
from app.repositories.dictionary_repository import DictionaryRepository
from app.repositories.game_repository import GameRepository


# --- _generate_feedback ---------------------------------------------------


@pytest.mark.parametrize(
    "guess, target, expected_colors",
    [
        ("apple", "apple", ["GREEN"] * 5),
        ("zzzzz", "apple", ["GRAY"] * 5),
        ("eppla", "apple", ["YELLOW", "GREEN", "GREEN", "GREEN", "YELLOW"]),
        # Duplicate letters: greens consume first, then yellows.
        ("allee", "apple", ["GREEN", "YELLOW", "GRAY", "GRAY", "GREEN"]),
        ("eerie", "apple", ["GRAY", "GRAY", "GRAY", "GRAY", "GREEN"]),
    ],
)
def test_generate_feedback(
    game_service: GameService,
    guess: str,
    target: str,
    expected_colors: list[str],
) -> None:
    feedback = game_service._generate_feedback(guess, target)
    assert [item["color"] for item in feedback] == expected_colors
    assert [item["letter"] for item in feedback] == list(guess)
    assert [item["index"] for item in feedback] == list(range(len(guess)))


# --- _resolve_status ------------------------------------------------------


def test_resolve_status_win(game_service: GameService) -> None:
    feedback = [{"letter": "a", "index": i, "color": "GREEN"} for i in range(5)]
    assert game_service._resolve_status(feedback, 1, 5) == GameStatus.WON


def test_resolve_status_win_on_last_guess(game_service: GameService) -> None:
    feedback = [{"letter": "a", "index": i, "color": "GREEN"} for i in range(5)]
    assert game_service._resolve_status(feedback, 6, 5) == GameStatus.WON


def test_resolve_status_loss_on_last_guess(game_service: GameService) -> None:
    feedback = [{"letter": "a", "index": i, "color": "GRAY"} for i in range(5)]
    assert game_service._resolve_status(feedback, 6, 5) == GameStatus.LOST


def test_resolve_status_in_progress(game_service: GameService) -> None:
    feedback = [{"letter": "a", "index": i, "color": "GRAY"} for i in range(5)]
    assert game_service._resolve_status(feedback, 3, 5) == GameStatus.IN_PROGRESS


# --- helpers --------------------------------------------------------------


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


async def _make_game(
    game_service: GameService,
    target: str = "apple",
) -> int:
    _seed_answer(target)
    game = await game_service.create_game(len(target))
    return game.id


# --- create_game ----------------------------------------------------------


async def test_create_game(
    game_service: GameService,
    dictionary_repo: DictionaryRepository,
) -> None:
    _seed_answer("apple")
    game = await game_service.create_game(5)
    assert game.word_length == 5
    assert game.target_word == "apple"
    assert game.status == GameStatus.IN_PROGRESS


# --- get_game -------------------------------------------------------------


async def test_get_game_not_found(game_service: GameService) -> None:
    with pytest.raises(GameNotFound):
        await game_service.get_game(999)


# --- submit_guess ---------------------------------------------------------


async def test_submit_guess_happy_path(
    game_service: GameService,
    dictionary_repo: DictionaryRepository,
) -> None:
    game_id = await _make_game(game_service)
    _seed_guess("eppla")

    guess = await game_service.submit_guess(game_id, "eppla")
    assert guess.word == "eppla"
    assert guess.guess_number == 1
    assert [item["color"] for item in guess.feedback] == [
        "YELLOW",
        "GREEN",
        "GREEN",
        "GREEN",
        "YELLOW",
    ]


async def test_submit_guess_normalizes_case(
    game_service: GameService,
    dictionary_repo: DictionaryRepository,
) -> None:
    game_id = await _make_game(game_service)
    _seed_guess("eppla")

    guess = await game_service.submit_guess(game_id, "EPPLA")
    assert guess.word == "eppla"


async def test_submit_guess_game_not_found(game_service: GameService) -> None:
    with pytest.raises(GameNotFound):
        await game_service.submit_guess(999, "apple")


async def test_submit_guess_wrong_length(
    game_service: GameService,
    dictionary_repo: DictionaryRepository,
) -> None:
    game_id = await _make_game(game_service)
    with pytest.raises(InvalidGuess):
        await game_service.submit_guess(game_id, "app")


async def test_submit_guess_not_in_dictionary(
    game_service: GameService,
    dictionary_repo: DictionaryRepository,
) -> None:
    game_id = await _make_game(game_service)
    with pytest.raises(InvalidGuess):
        await game_service.submit_guess(game_id, "zzzzz")


async def test_submit_guess_win(
    game_service: GameService,
    dictionary_repo: DictionaryRepository,
) -> None:
    game_id = await _make_game(game_service)
    _seed_guess("apple")

    await game_service.submit_guess(game_id, "apple")
    game = await game_service.get_game(game_id)
    assert game.status == GameStatus.WON


async def test_submit_guess_after_finished(
    game_service: GameService,
    dictionary_repo: DictionaryRepository,
) -> None:
    game_id = await _make_game(game_service)
    _seed_guess("apple")

    await game_service.submit_guess(game_id, "apple")
    with pytest.raises(GameAlreadyFinished):
        await game_service.submit_guess(game_id, "apple")


async def test_submit_guess_loss_after_max_attempts(
    game_service: GameService,
    dictionary_repo: DictionaryRepository,
) -> None:
    game_id = await _make_game(game_service)
    _seed_guess("eppla")

    for _ in range(6):
        await game_service.submit_guess(game_id, "eppla")

    game = await game_service.get_game(game_id)
    assert game.status == GameStatus.LOST
    assert len(game.guesses) == 6
