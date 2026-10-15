from __future__ import annotations


class DomainError(Exception):
    """Base class for domain-level errors raised by the application layer."""


class GameNotFound(DomainError):
    """Raised when a game with the given id does not exist."""


class GameAlreadyFinished(DomainError):
    """Raised when a guess is submitted against a finished game."""


class InvalidGuess(DomainError):
    """Raised when a guess is malformed or not a valid dictionary word."""
