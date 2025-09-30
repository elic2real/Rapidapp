from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.development,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class RequestLog(Base):
    """Model for logging AI requests and responses."""
    __tablename__ = "request_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=True, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    model_name = Column(String(255), nullable=False, index=True)
    provider = Column(String(100), nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    cache_hit = Column(Boolean, default=False, index=True)
    success = Column(Boolean, default=True, index=True)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class SemanticCacheEntry(Base):
    """Model for semantic cache entries."""
    __tablename__ = "semantic_cache_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_hash = Column(String(64), nullable=False, unique=True, index=True)
    prompt_text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=False)  # Store as JSON array
    response = Column(Text, nullable=False)
    model_name = Column(String(255), nullable=False, index=True)
    tokens_used = Column(Integer, nullable=True)
    hit_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)


class ModelMetrics(Base):
    """Model for storing model performance metrics."""
    __tablename__ = "model_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(255), nullable=False, index=True)
    provider = Column(String(100), nullable=False, index=True)
    avg_latency_ms = Column(Float, nullable=False)
    success_rate = Column(Float, nullable=False)
    tokens_per_second = Column(Float, nullable=True)
    error_rate = Column(Float, nullable=False)
    total_requests = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


async def create_tables() -> None:
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """Get database session dependency."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
