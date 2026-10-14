from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.cache import redis_client
from app.db import engine, init_db
from app.dictionary import ensure_words_json, seed_dictionary


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    try:
        await redis_client.ping()
        ensure_words_json()
        await seed_dictionary(redis_client)
    except Exception as exc:  # noqa: BLE001
        print(f"Dictionary seeding failed on startup: {exc}")
    yield
    await engine.dispose()
    await redis_client.aclose()


app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
