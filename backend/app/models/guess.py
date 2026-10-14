from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Literal, TypedDict

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.game import Game


FeedbackColor = Literal["GRAY", "YELLOW", "GREEN"]


class FeedbackItem(TypedDict):
    letter: str
    index: int
    color: FeedbackColor


class Guess(Base):
    __tablename__ = "guesses"
    __table_args__ = (
        UniqueConstraint("game_id", "guess_number", name="uq_guesses_game_id_guess_number"),
        CheckConstraint("json_valid(feedback)", name="ck_guesses_feedback_valid_json"),
        CheckConstraint("json_type(feedback) = 'array'", name="ck_guesses_feedback_is_array"),
        CheckConstraint(
            "json_array_length(feedback) = length(word)",
            name="ck_guesses_feedback_length_matches_word",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True
    )
    word: Mapped[str] = mapped_column(String(8), nullable=False)
    guess_number: Mapped[int] = mapped_column(Integer, nullable=False)
    feedback: Mapped[list[FeedbackItem]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    game: Mapped[Game] = relationship(back_populates="guesses")
