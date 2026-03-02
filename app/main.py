from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings


def _ensure_upload_directories() -> None:
    for folder in ["uploads", "uploads/avatars", "uploads/it-asset", "uploads/knowledge-books"]:
        Path(folder).mkdir(parents=True, exist_ok=True)


def create_app() -> FastAPI:
    _ensure_upload_directories()

    app = FastAPI(title="YTRC Center API (FastAPI)", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins if settings.cors_origins else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_prefix)
    app.mount(f"{settings.api_prefix}/uploads", StaticFiles(directory="uploads"), name="uploads")

    # Mount Socket.io
    from app.core.socket_manager import socket_app
    app.mount("/", socket_app)

    return app


app = create_app()
