from __future__ import annotations

from httpx import AsyncClient

from app.repositories.dictionary_repository import DictionaryRepository


async def _seed_answer(
    dictionary_repo: DictionaryRepository, word: str
) -> None:
    await dictionary_repo._client.rpush(f"dict:answer:{len(word)}", word)


async def _seed_guess(
    dictionary_repo: DictionaryRepository, word: str
) -> None:
    await dictionary_repo._client.sadd(f"dict:guess:{len(word)}", word)


async def test_create_game(
    client: AsyncClient, dictionary_repo: DictionaryRepository
) -> None:
    await _seed_answer(dictionary_repo, "apple")
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
    await _seed_answer(dictionary_repo, "apple")
    await client.post("/games", json={"word_length": 5})
    await client.post("/games", json={"word_length": 5})

    response = await client.get("/games")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert body["limit"] == 20
    assert body["offset"] == 0


async def test_get_game(
    client: AsyncClient, dictionary_repo: DictionaryRepository
) -> None:
    await _seed_answer(dictionary_repo, "apple")
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
    await _seed_answer(dictionary_repo, "apple")
    await _seed_guess(dictionary_repo, "eppla")
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
    await _seed_answer(dictionary_repo, "apple")
    created = await client.post("/games", json={"word_length": 5})
    game_id = created.json()["id"]

    response = await client.post(
        f"/games/{game_id}/guesses", json={"word": "zzzzz"}
    )
    assert response.status_code == 422


async def test_submit_guess_after_finished(
    client: AsyncClient, dictionary_repo: DictionaryRepository
) -> None:
    await _seed_answer(dictionary_repo, "apple")
    await _seed_guess(dictionary_repo, "apple")
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
