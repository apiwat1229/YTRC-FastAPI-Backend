from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


def _ensure_upload_directories() -> None:
    for folder in [
        "uploads",
        "uploads/avatars",
        "uploads/it-asset",
        "uploads/knowledge-books",
    ]:
        Path(folder).mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import all models so Base.metadata is populated before create_all
    import app.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


def create_app() -> FastAPI:
    _ensure_upload_directories()

    is_production = settings.environment == "production"

    limiter = Limiter(key_func=get_remote_address)
    app = FastAPI(
        title="YTRC Center API (FastAPI)",
        version="1.0.0",
        lifespan=lifespan,
        # ปิด docs ใน production เพื่อความปลอดภัย
        docs_url=None if is_production else "/docs",
        redoc_url=None if is_production else "/redoc",
        openapi_url=None if is_production else "/openapi.json",
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    cors_origins = settings.cors_origins or ["http://localhost:3000"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_prefix)
    app.mount(
        f"{settings.api_prefix}/uploads",
        StaticFiles(directory="uploads"),
        name="uploads",
    )

    # Mount Socket.io
    from app.core.socket_manager import socket_app

    app.mount("/", socket_app)

    return app


app = create_app()
