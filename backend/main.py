import logging
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.routes import games
from app.cache import redis_client
from app.db import engine, init_db
from app.dictionary import ensure_words_json, seed_dictionary
from app.models.errors import GameAlreadyFinished, GameNotFound, InvalidGuess

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    try:
        await redis_client.ping()
        ensure_words_json()
        await seed_dictionary(redis_client)
    except (redis.RedisError, OSError) as exc:
        logger.warning("Dictionary seeding failed on startup: %s", exc)
    yield
    await engine.dispose()
    await redis_client.aclose()


app = FastAPI(lifespan=lifespan)

# Configure CORS. The regex covers GitHub Codespaces forwarded frontend
# origins (https://<codespace>-5173.app.github.dev), which change per
# codespace, while the explicit origin covers local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_origin_regex=r"https://.*-5173\.app\.github\.dev",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(GameNotFound)
async def _game_not_found_handler(request: Request, exc: GameNotFound) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(GameAlreadyFinished)
async def _game_already_finished_handler(
    request: Request, exc: GameAlreadyFinished
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(InvalidGuess)
async def _invalid_guess_handler(request: Request, exc: InvalidGuess) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


app.include_router(games.router, prefix="/games", tags=["games"])


@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    db_status = "ok"
    redis_status = "ok"

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001
        db_status = "error"

    try:
        await redis_client.ping()
    except Exception:  # noqa: BLE001
        redis_status = "error"

    return {"status": "healthy", "db": db_status, "redis": redis_status}
