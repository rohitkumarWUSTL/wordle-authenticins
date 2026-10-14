from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.game import GameStatus
from app.models.guess import FeedbackItem


class CreateGameRequest(BaseModel):
    word_length: int = Field(..., ge=5, le=8)


class GuessRequest(BaseModel):
    word: str


class GuessResponse(BaseModel):
    word: str
    guess_number: int
    feedback: list[FeedbackItem]


class GameResponse(BaseModel):
    id: int
    word_length: int
    status: GameStatus
    created_at: datetime
    updated_at: datetime
    guesses: list[GuessResponse] = []


class GameListResponse(BaseModel):
    items: list[GameResponse]
    total: int
    limit: int
    offset: int
