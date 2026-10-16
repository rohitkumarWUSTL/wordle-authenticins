from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game import Game, GameStatus
from app.models.guess import FeedbackItem, Guess


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

    async def list(
        self,
        limit: int,
        offset: int,
        status: GameStatus | None = None,
    ) -> tuple[list[Game], int]:
        count_query = select(func.count()).select_from(Game)
        list_query = select(Game)
        if status is not None:
            count_query = count_query.where(Game.status == status)
            list_query = list_query.where(Game.status == status)

        total = await self._session.scalar(count_query)
        result = await self._session.scalars(
            list_query
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
        feedback: list[FeedbackItem],
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
        # The game's `guesses` collection was loaded before the new guess
        # was inserted, so refresh it to pick up the new row. Without this
        # the returned game lags one guess behind.
        await self._session.refresh(game, ["guesses"])
        return guess
