from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.api.schemas.game import (
    CreateGameRequest,
    GameListResponse,
    GameResponse,
    GuessRequest,
)
from app.application.game_service import GameService
from app.dependencies import get_game_service
from app.models.game import Game, GameStatus

router = APIRouter()


def _to_response(game: Game) -> GameResponse:
    """Serialize a game, hiding the target word while it's in progress."""
    response = GameResponse.model_validate(game)
    if game.status == GameStatus.IN_PROGRESS:
        response.target_word = None
    return response


@router.post("", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(
    payload: CreateGameRequest,
    service: GameService = Depends(get_game_service),
) -> GameResponse:
    game = await service.create_game(payload.word_length)
    return _to_response(game)


@router.get("", response_model=GameListResponse)
async def list_games(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: GameStatus | None = Query(None),
    service: GameService = Depends(get_game_service),
) -> GameListResponse:
    items, total = await service.list_games(limit, offset, status)
    return GameListResponse(
        items=[_to_response(game) for game in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: int,
    service: GameService = Depends(get_game_service),
) -> GameResponse:
    game = await service.get_game(game_id)
    return _to_response(game)


@router.post("/{game_id}/guesses", response_model=GameResponse)
async def submit_guess(
    game_id: int,
    payload: GuessRequest,
    service: GameService = Depends(get_game_service),
) -> GameResponse:
    game = await service.submit_guess(game_id, payload.word)
    return _to_response(game)


@router.post("/{game_id}/give-up", response_model=GameResponse)
async def give_up(
    game_id: int,
    service: GameService = Depends(get_game_service),
) -> GameResponse:
    game = await service.give_up(game_id)
    return _to_response(game)
