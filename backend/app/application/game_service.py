from __future__ import annotations

from app.models.game import Game
from app.models.guess import Guess
from app.repositories.dictionary_repository import DictionaryRepository
from app.repositories.game_repository import GameRepository


class GameService:
    def __init__(
        self,
        games: GameRepository,
        dictionary: DictionaryRepository,
    ) -> None:
        self._games = games
        self._dictionary = dictionary

    async def create_game(self, word_length: int) -> Game:
        raise NotImplementedError

    async def get_game(self, game_id: int) -> Game:
        raise NotImplementedError

    async def list_games(self, limit: int, offset: int) -> tuple[list[Game], int]:
        raise NotImplementedError

    async def submit_guess(self, game_id: int, word: str) -> Guess:
        raise NotImplementedError
