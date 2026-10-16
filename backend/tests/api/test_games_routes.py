from __future__ import annotations

from httpx import AsyncClient

from app.repositories.dictionary_repository import DictionaryRepository
from tests._words import seed_answer, seed_empty, seed_guess


async def test_create_game(
    client: AsyncClient, dictionary_repo: DictionaryRepository
) -> None:
    seed_answer("apple")
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
    seed_answer("apple")
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
    seed_answer("apple")
    seed_guess("apple")

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
    seed_answer("apple")
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
    seed_answer("apple")
    seed_guess("eppla")
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
    seed_answer("apple")
    created = await client.post("/games", json={"word_length": 5})
    game_id = created.json()["id"]

    # Explicitly seed an empty guess list so the assertion doesn't depend on
    # what the answer-seeding helper happens to write.
    seed_empty(5)
    response = await client.post(
        f"/games/{game_id}/guesses", json={"word": "zzzzz"}
    )
    assert response.status_code == 422


async def test_submit_guess_after_finished(
    client: AsyncClient, dictionary_repo: DictionaryRepository
) -> None:
    seed_answer("apple")
    seed_guess("apple")
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


async def test_give_up(
    client: AsyncClient, dictionary_repo: DictionaryRepository
) -> None:
    seed_answer("apple")
    created = await client.post("/games", json={"word_length": 5})
    game_id = created.json()["id"]

    response = await client.post(f"/games/{game_id}/give-up")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == game_id
    assert body["status"] == "LOST"
    assert body["target_word"] == "apple"


async def test_give_up_not_found(client: AsyncClient) -> None:
    response = await client.post("/games/999/give-up")
    assert response.status_code == 404


async def test_give_up_after_finished(
    client: AsyncClient, dictionary_repo: DictionaryRepository
) -> None:
    seed_answer("apple")
    seed_guess("apple")
    created = await client.post("/games", json={"word_length": 5})
    game_id = created.json()["id"]

    first = await client.post(
        f"/games/{game_id}/guesses", json={"word": "apple"}
    )
    assert first.status_code == 200

    response = await client.post(f"/games/{game_id}/give-up")
    assert response.status_code == 409
