from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.constants import MAX_WORD_LENGTH, MIN_WORD_LENGTH
from app.models.game import GameStatus
from app.models.guess import FeedbackItem


class CreateGameRequest(BaseModel):
    word_length: int = Field(..., ge=MIN_WORD_LENGTH, le=MAX_WORD_LENGTH)


class GuessRequest(BaseModel):
    word: str

    @field_validator("word")                                                                                                                                                                                  
    @classmethod                                                                                                                                                                                              
    def validate_word_length(cls, v: str) -> str:                                                                                                                                                             
        if not (MIN_WORD_LENGTH <= len(v) <= MAX_WORD_LENGTH):                                                                                                                                                
            raise ValueError(                                                                                                                                                                                 
                f"Invalid word length"                                                                                                                    
            )                                                                                                                                                                                                 
        return v 

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
