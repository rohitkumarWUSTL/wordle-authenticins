from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game import Game, GameStatus
from app.models.guess import Guess


class GameRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, word_length: int, target_word: str) -> Game:
        game = Game(
            word_length=word_length,
            target_word=target_word,
            status=GameStatus.IN_PROGRESS,
        )
        self._session.add(game)
        await self._session.commit()
        await self._session.refresh(game)
        return game

    async def get(self, game_id: int) -> Game | None:
        return await self._session.get(Game, game_id)

    async def list(self, limit: int, offset: int) -> tuple[list[Game], int]:
        total = await self._session.scalar(select(func.count()).select_from(Game))
        result = await self._session.scalars(
            select(Game)
            .order_by(Game.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result), total or 0

    async def add_guess(
        self,
        game: Game,
        word: str,
        guess_number: int,
        feedback: list,
        status: GameStatus,
    ) -> Guess:
        guess = Guess(
            game_id=game.id,
            word=word,
            guess_number=guess_number,
            feedback=feedback,
        )
        self._session.add(guess)
        game.status = status
        await self._session.commit()
        await self._session.refresh(guess)
        return guess
