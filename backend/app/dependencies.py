from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.game_service import GameService
from app.db import get_db
from app.repositories.dictionary_repository import DictionaryRepository
from app.repositories.game_repository import GameRepository


async def get_game_service(
    session: AsyncSession = Depends(get_db),
) -> GameService:
    return GameService(
        games=GameRepository(session),
        dictionary=DictionaryRepository(),
    )
