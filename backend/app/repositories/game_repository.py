from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game import Game, GameStatus
from app.models.guess import Guess


class GameRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, word_length: int, target_word: str) -> Game:
        raise NotImplementedError

    async def get(self, game_id: int) -> Game | None:
        raise NotImplementedError

    async def list(self, limit: int, offset: int) -> tuple[list[Game], int]:
        raise NotImplementedError

    async def add_guess(
        self,
        game: Game,
        word: str,
        guess_number: int,
        feedback: list,
        status: GameStatus,
    ) -> Guess:
        raise NotImplementedError
