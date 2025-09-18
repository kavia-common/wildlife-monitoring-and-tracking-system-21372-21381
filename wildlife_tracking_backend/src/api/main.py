from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.db.connection import ensure_database, close_database, init_indexes, get_settings

openapi_tags = [
    {"name": "health", "description": "Service and database health checks"},
    {"name": "info", "description": "API information and configuration details"},
]

app = FastAPI(
    title="Wildlife Tracking Backend",
    description="Core API for wildlife tracking and monitoring with MongoDB storage.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    """
    Connect to MongoDB and initialize indexes on startup.
    """
    await ensure_database()
    await init_indexes()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """
    Close MongoDB connections on shutdown.
    """
    await close_database()


@app.get("/", tags=["health"], summary="Health Check", description="Basic service health check.")
def health_check():
    return {"message": "Healthy"}


class DBHealthResponse(BaseModel):
    status: str
    db_name: str


@app.get(
    "/health/db",
    tags=["health"],
    summary="Database Health",
    description="Check MongoDB connectivity and return the configured database name.",
    response_model=DBHealthResponse,
)
async def db_health():
    """
    PUBLIC_INTERFACE
    Returns database health status.

    - status: 'ok' if ping to the database succeeds
    - db_name: currently configured database name
    """
    db = await ensure_database()
    await db.command("ping")
    settings = get_settings()
    return DBHealthResponse(status="ok", db_name=settings.MONGODB_DB_NAME)


@app.get(
    "/info",
    tags=["info"],
    summary="Service Info",
    description="Get information about the API and database configuration (non-sensitive).",
)
def service_info():
    """
    PUBLIC_INTERFACE
    Provides non-sensitive service information useful for diagnostics.
    """
    settings = get_settings()
    return {
        "name": "wildlife_tracking_backend",
        "database": {
            "type": "mongodb",
            "db_name": settings.MONGODB_DB_NAME,
            "uri_set": bool(settings.MONGODB_URI),
        },
        "version": app.version,
    }
