from __future__ import annotations

from collections import Counter

from app.models.errors import (
    GameAlreadyFinished,
    GameNotFound,
    InvalidGuess,
)
from app.models.game import Game, GameStatus
from app.models.guess import FeedbackItem, Guess
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
        target_word = await self._dictionary.random_answer(word_length)
        return await self._games.create(word_length, target_word)

    async def get_game(self, game_id: int) -> Game:
        game = await self._games.get(game_id)
        if game is None:
            raise GameNotFound(f"Game {game_id} not found")
        return game

    async def list_games(self, limit: int, offset: int) -> tuple[list[Game], int]:
        return await self._games.list(limit, offset)

    async def submit_guess(self, game_id: int, word: str) -> Guess:
        game = await self._games.get(game_id)
        if game is None:
            raise GameNotFound(f"Game {game_id} not found")
        if game.status != GameStatus.IN_PROGRESS:
            raise GameAlreadyFinished(f"Game {game_id} is already finished")

        word = await self._validate_guess(word, game.word_length)
        feedback = self._generate_feedback(word, game.target_word)
        guess_number = len(game.guesses) + 1
        status = self._resolve_status(feedback, guess_number, game.word_length)

        return await self._games.add_guess(
            game, word, guess_number, feedback, status
        )

    async def _validate_guess(self, word: str, length: int) -> str:
        word = word.lower()
        if len(word) != length:
            raise InvalidGuess(
                f"Guess must be {length} letters long, got {len(word)}"
            )
        if not await self._dictionary.is_valid(word, length):
            raise InvalidGuess(f"'{word}' is not a valid word")
        return word

    def _generate_feedback(
        self, guess: str, target: str
    ) -> list[FeedbackItem]:
        feedback: list[FeedbackItem] = [
            {"letter": letter, "index": i, "color": "GRAY"}
            for i, letter in enumerate(guess)
        ]
        remaining = Counter(target)

        # First pass: greens consume their letters from the pool.
        for i, (g, t) in enumerate(zip(guess, target)):
            if g == t:
                feedback[i]["color"] = "GREEN"
                remaining[g] -= 1

        # Second pass: promote grays to yellows where letters remain.
        for i, g in enumerate(guess):
            if feedback[i]["color"] == "GRAY" and remaining[g] > 0:
                feedback[i]["color"] = "YELLOW"
                remaining[g] -= 1

        return feedback

    def _resolve_status(
        self,
        feedback: list[FeedbackItem],
        guess_number: int,
        word_length: int,
    ) -> GameStatus:
        if all(item["color"] == "GREEN" for item in feedback):
            return GameStatus.WON
        if guess_number >= word_length + 1:
            return GameStatus.LOST
        return GameStatus.IN_PROGRESS
