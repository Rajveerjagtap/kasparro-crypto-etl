"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.routes import router
from app.core.config import settings
from app.core.logging import logger
from app.core.middleware import MetricsMiddleware, RequestLoggingMiddleware
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown."""
    logger.info("Starting Kasparro application")
    # Database tables are managed by Alembic migrations
    # No need for create_all - it can cause duplicate type errors
    logger.info("Database connection established")
    yield
    await engine.dispose()
    logger.info("Kasparro application shutdown complete")


app = FastAPI(
    title=settings.app_name,
    description="Crypto Data ETL & API Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Add observability middleware (order matters: last added = first executed)
app.add_middleware(MetricsMiddleware)
app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    from datetime import datetime, timezone
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
