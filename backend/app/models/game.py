from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import MAX_WORD_LENGTH
from app.db import Base

if TYPE_CHECKING:
    from app.models.guess import Guess


class GameStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    WON = "WON"
    LOST = "LOST"


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    word_length: Mapped[int] = mapped_column(Integer, nullable=False)
    target_word: Mapped[str] = mapped_column(String(MAX_WORD_LENGTH), nullable=False)
    status: Mapped[GameStatus] = mapped_column(
        Enum(GameStatus, native_enum=False, length=16),
        nullable=False,
        default=GameStatus.IN_PROGRESS,
        server_default=GameStatus.IN_PROGRESS.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    guesses: Mapped[list[Guess]] = relationship(
        back_populates="game",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Guess.guess_number",
    )
