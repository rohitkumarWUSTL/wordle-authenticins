"""Lightweight tests for the guess submission endpoint.

The guess endpoint returns the full updated game (not just the new guess)
so the frontend doesn't need a follow-up GET. These tests pin that
contract by swapping in a fake GameService, so they exercise the route's
serialization (the GameResponse shape and the target_word hiding) without
needing a DB or the dictionary.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies import get_game_service
from app.models.game import Game, GameStatus
from app.models.guess import Guess
from main import app


class FakeGameService:
    """Minimal stand-in for GameService that returns a pre-built Game."""

    def __init__(self, game: Game) -> None:
        self._game = game

    async def submit_guess(self, game_id: int, word: str) -> Game:
        return self._game


def _make_game(status: GameStatus = GameStatus.IN_PROGRESS) -> Game:
    now = datetime.now(timezone.utc)
    game = Game(
        id=1,
        word_length=5,
        target_word="crane",
        status=status,
        created_at=now,
        updated_at=now,
    )
    game.guesses = [
        Guess(
            id=1,
            game_id=1,
            word="slate",
            guess_number=1,
            feedback=[
                {"letter": "s", "index": 0, "color": "GRAY"},
                {"letter": "l", "index": 1, "color": "GRAY"},
                {"letter": "a", "index": 2, "color": "YELLOW"},
                {"letter": "t", "index": 3, "color": "GRAY"},
                {"letter": "e", "index": 4, "color": "GREEN"},
            ],
        )
    ]
    return game


@pytest.fixture
def client_factory() -> Iterator:
    def _make(game: Game) -> AsyncClient:
        app.dependency_overrides[get_game_service] = lambda: FakeGameService(game)
        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://test")

    yield _make
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_submit_guess_hides_target_word_while_in_progress(client_factory):
    game = _make_game(status=GameStatus.IN_PROGRESS)
    async with client_factory(game) as client:
        response = await client.post("/games/1/guesses", json={"word": "slate"})

    assert response.status_code == 200
    assert response.json()["target_word"] is None


@pytest.mark.asyncio
async def test_submit_guess_reveals_target_word_when_finished(client_factory):
    game = _make_game(status=GameStatus.WON)
    async with client_factory(game) as client:
        response = await client.post("/games/1/guesses", json={"word": "slate"})

    assert response.status_code == 200
    assert response.json()["target_word"] == "crane"
