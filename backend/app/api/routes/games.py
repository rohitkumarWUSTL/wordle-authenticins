from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.schemas.game import (
    CreateGameRequest,
    GameListResponse,
    GameResponse,
    GuessRequest,
    GuessResponse,
)
from app.application.game_service import GameService
from app.dependencies import get_game_service

router = APIRouter()


@router.post("", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(
    payload: CreateGameRequest,
    service: GameService = Depends(get_game_service),
) -> GameResponse:
    raise NotImplementedError


@router.get("", response_model=GameListResponse)
async def list_games(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: GameService = Depends(get_game_service),
) -> GameListResponse:
    raise NotImplementedError


@router.get("/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: int,
    service: GameService = Depends(get_game_service),
) -> GameResponse:
    raise NotImplementedError


@router.post("/{game_id}/guesses", response_model=GuessResponse)
async def submit_guess(
    game_id: int,
    payload: GuessRequest,
    service: GameService = Depends(get_game_service),
) -> GuessResponse:
    raise NotImplementedError
