from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app import dictionary
from app.application.game_service import GameService
from app.db import Base, get_db
from app.repositories.dictionary_repository import DictionaryRepository
from app.repositories.game_repository import GameRepository


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(dictionary, "DATA_DIR", tmp_path)
    dictionary._load_words.cache_clear()
    dictionary._load_scrabble_words.cache_clear()
    yield tmp_path
    dictionary._load_words.cache_clear()
    dictionary._load_scrabble_words.cache_clear()


@pytest.fixture
async def game_repo(db_session: AsyncSession) -> GameRepository:
    return GameRepository(db_session)


@pytest.fixture
async def dictionary_repo(data_dir: Path) -> DictionaryRepository:
    return DictionaryRepository()


@pytest.fixture
async def game_service(
    game_repo: GameRepository,
    dictionary_repo: DictionaryRepository,
) -> GameService:
    return GameService(games=game_repo, dictionary=dictionary_repo)


@pytest.fixture
async def client(
    db_session: AsyncSession,
    data_dir: Path,
) -> AsyncGenerator[AsyncClient, None]:
    from main import app

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
