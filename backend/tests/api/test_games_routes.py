from __future__ import annotations

from pathlib import Path

from httpx import AsyncClient

from app import dictionary
from app.repositories.dictionary_repository import DictionaryRepository


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


async def test_create_game(
    client: AsyncClient, dictionary_repo: DictionaryRepository
) -> None:
    _seed_answer("apple")
    response = await client.post("/games", json={"word_length": 5})
    assert response.status_code == 201
    body = response.json()
    assert body["word_length"] == 5
    assert body["status"] == "IN_PROGRESS"
    assert body["guesses"] == []


async def test_create_game_invalid_length(client: AsyncClient) -> None:
    response = await client.post("/games", json={"word_length": 1})
    assert response.status_code == 422


async def test_list_games(
    client: AsyncClient, dictionary_repo: DictionaryRepository
) -> None:
    _seed_answer("apple")
    await client.post("/games", json={"word_length": 5})
    await client.post("/games", json={"word_length": 5})

    response = await client.get("/games")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert body["limit"] == 20
    assert body["offset"] == 0


async def test_list_games_filter_by_status(
    client: AsyncClient, dictionary_repo: DictionaryRepository
) -> None:
    _seed_answer("apple")
    _seed_guess("apple")

    in_progress = await client.post("/games", json={"word_length": 5})
    finished = await client.post("/games", json={"word_length": 5})
    finished_id = finished.json()["id"]

    # Finish one game by guessing the answer.
    await client.post(
        f"/games/{finished_id}/guesses", json={"word": "apple"}
    )

    response = await client.get("/games", params={"status": "IN_PROGRESS"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == in_progress.json()["id"]
    assert body["items"][0]["status"] == "IN_PROGRESS"

    response = await client.get("/games", params={"status": "WON"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == finished_id

    response = await client.get("/games")
    assert response.status_code == 200
    assert response.json()["total"] == 2


async def test_list_games_invalid_status(client: AsyncClient) -> None:
    response = await client.get("/games", params={"status": "BOGUS"})
    assert response.status_code == 422


async def test_get_game(
    client: AsyncClient, dictionary_repo: DictionaryRepository
) -> None:
    _seed_answer("apple")
    created = await client.post("/games", json={"word_length": 5})
    game_id = created.json()["id"]

    response = await client.get(f"/games/{game_id}")
    assert response.status_code == 200
    assert response.json()["id"] == game_id


async def test_get_game_not_found(client: AsyncClient) -> None:
    response = await client.get("/games/999")
    assert response.status_code == 404


async def test_submit_guess(
    client: AsyncClient, dictionary_repo: DictionaryRepository
) -> None:
    _seed_answer("apple")
    _seed_guess("eppla")
    created = await client.post("/games", json={"word_length": 5})
    game_id = created.json()["id"]

    response = await client.post(
        f"/games/{game_id}/guesses", json={"word": "eppla"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["word"] == "eppla"
    assert body["guess_number"] == 1
    assert [item["color"] for item in body["feedback"]] == [
        "YELLOW",
        "GREEN",
        "GREEN",
        "GREEN",
        "YELLOW",
    ]


async def test_submit_guess_game_not_found(client: AsyncClient) -> None:
    response = await client.post("/games/999/guesses", json={"word": "apple"})
    assert response.status_code == 404


async def test_submit_guess_invalid_word(
    client: AsyncClient, dictionary_repo: DictionaryRepository
) -> None:
    _seed_answer("apple")
    created = await client.post("/games", json={"word_length": 5})
    game_id = created.json()["id"]

    response = await client.post(
        f"/games/{game_id}/guesses", json={"word": "zzzzz"}
    )
    assert response.status_code == 422


async def test_submit_guess_after_finished(
    client: AsyncClient, dictionary_repo: DictionaryRepository
) -> None:
    _seed_answer("apple")
    _seed_guess("apple")
    created = await client.post("/games", json={"word_length": 5})
    game_id = created.json()["id"]

    first = await client.post(
        f"/games/{game_id}/guesses", json={"word": "apple"}
    )
    assert first.status_code == 200

    second = await client.post(
        f"/games/{game_id}/guesses", json={"word": "apple"}
    )
    assert second.status_code == 409
