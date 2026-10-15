from __future__ import annotations

from app.models.game import GameStatus
from app.repositories.game_repository import GameRepository


async def test_create_and_get(game_repo: GameRepository) -> None:
    game = await game_repo.create(5, "apple")
    assert game.id is not None

    fetched = await game_repo.get(game.id)
    assert fetched is not None
    assert fetched.target_word == "apple"


async def test_get_missing(game_repo: GameRepository) -> None:
    assert await game_repo.get(999) is None


async def test_list_pagination(game_repo: GameRepository) -> None:
    for _ in range(3):
        await game_repo.create(5, "apple")

    items, total = await game_repo.list(limit=2, offset=0)
    assert total == 3
    assert len(items) == 2

    items, total = await game_repo.list(limit=2, offset=2)
    assert total == 3
    assert len(items) == 1


async def test_add_guess_updates_status(game_repo: GameRepository) -> None:
    game = await game_repo.create(5, "apple")
    feedback = [{"letter": "a", "index": i, "color": "GREEN"} for i in range(5)]

    guess = await game_repo.add_guess(
        game, "apple", 1, feedback, GameStatus.WON
    )
    assert guess.id is not None

    refreshed = await game_repo.get(game.id)
    assert refreshed is not None
    assert refreshed.status == GameStatus.WON
