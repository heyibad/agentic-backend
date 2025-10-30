import os
from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
from app.core.config import settings
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

load_dotenv()

# Get DATABASE_URL from settings or environment
DATABASE_URL = settings.database_url or os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment or config")

# Convert postgres:// to postgresql+asyncpg:// for async support
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Parse URL and handle SSL parameters for asyncpg
parsed_url = urlparse(DATABASE_URL)
query_params = parse_qs(parsed_url.query)

# Convert sslmode to ssl parameter for asyncpg
connect_args = {}
if "sslmode" in query_params:
    sslmode = query_params["sslmode"][0]
    # Remove sslmode and channel_binding from query string
    query_params.pop("sslmode", None)
    query_params.pop("channel_binding", None)

    # Set ssl=True for asyncpg if sslmode is require or verify-*
    if sslmode in ["require", "verify-ca", "verify-full"]:
        connect_args["ssl"] = "require"

    # Rebuild URL without sslmode
    new_query = urlencode(query_params, doseq=True)
    DATABASE_URL = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment,
        )
    )

# Create async engine with optimized connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to False to reduce log noise
    future=True,
    pool_size=20,  # Increased from default 5
    max_overflow=40,  # Allow up to 60 total connections
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args=connect_args,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.

    Usage:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSession(engine) as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables. Use for development only."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
